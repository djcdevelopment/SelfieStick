using System;
using System.Collections;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using UnityEngine;

namespace CameraProof
{
    public sealed partial class Plugin
    {
        public const string CaptureVersion = "0.3.3";

        private static string WorldFile(World world) => typeof(World).GetField("m_worldName",
            System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic
            | System.Reflection.BindingFlags.Instance)?.GetValue(world) as string;

        private static float Finite(string text)
        {
            var value = P(text);
            if (float.IsNaN(value) || float.IsInfinity(value)) throw new FormatException("Non-finite camera value");
            return value;
        }

        private static Shot ExtendShot(Shot shot, string[] fields)
        {
            if (fields.Length > 16 && !string.IsNullOrWhiteSpace(fields[16]))
            {
                if (fields.Length < 22) throw new FormatException("Exact lens requires lens xyz, vertical FOV, width and height");
                shot.Lens = new Vector3(Finite(fields[16]), Finite(fields[17]), Finite(fields[18]));
            }
            if (fields.Length > 19 && !string.IsNullOrWhiteSpace(fields[19]))
            {
                shot.VerticalFov = Finite(fields[19]);
                if (shot.VerticalFov < 1 || shot.VerticalFov > 179) throw new FormatException("Vertical FOV must be 1..179");
            }
            if (fields.Length > 20 && !string.IsNullOrWhiteSpace(fields[20]))
            {
                shot.Width = int.Parse(fields[20], CultureInfo.InvariantCulture);
                shot.Height = int.Parse(fields[21], CultureInfo.InvariantCulture);
                if (shot.Width < 64 || shot.Height < 64 || shot.Width > 3840 || shot.Height > 3840)
                    throw new FormatException("Capture dimensions must be 64..3840");
            }
            if (fields.Length > 22 && !string.IsNullOrWhiteSpace(fields[22])) shot.Roll = Finite(fields[22]);
            if (shot.Lens.HasValue && (!shot.VerticalFov.HasValue || shot.Width == 0))
                throw new FormatException("Exact lens requires projection settings");
            if (shot.Mode == "exact" && !shot.Lens.HasValue) throw new FormatException("Exact shot has no lens");
            return shot;
        }

        private IEnumerator RunExactShot(Shot shot, string run, string directory, string plan)
        {
            var prefix = "{\"run\":" + JsonString(run) + ",\"plan\":" + JsonString(plan)
                + ",\"cluster_id\":" + shot.ClusterId + ",\"shot\":" + JsonString(shot.Name)
                + ",\"plugin_version\":" + JsonString(CaptureVersion) + ",\"exact\":true,";
            var player = GetLocalPlayer();
            if (player == null)
            {
                AppendReceipt(prefix + "\"skipped\":\"player_unavailable\"}");
                yield break;
            }
            // Streaming is anchored by the feet; it never determines the authored lens.
            var feet = shot.Lens.Value - Vector3.up * 1.7f;
            SetInvulnerable(player, true);
            PlacePlayer(player, feet);
            _holdAt = feet;
            TryAim(shot.Yaw, shot.Pitch);
            SetForcedEnvironment(shot.Environment);
            SetDebugTime(shot.TimeOfDay);
            yield return WaitForStablePlayer(feet, 15f);
            yield return WaitForWorld(shot.Aim, 25f);
            HoldFiresLit(shot.Aim, FireSweepRadius, Mathf.Max(100f, Vector3.Distance(feet, shot.Aim) + 80f), shot.Fires);
            yield return new WaitForSeconds(Mathf.Max(1f, _settleSeconds.Value));
            if (!_lastWorldSettled || PiecesNear(shot.Aim, 60f) <= 0)
            {
                AppendReceipt(prefix + "\"skipped\":\"world_never_loaded\"}");
                if (shot.Fires) ReleaseHeldLight();
                yield break;
            }
            if (Physics.CheckSphere(shot.Lens.Value, .08f,
                    LayerMask.GetMask("terrain", "static_solid", "Default", "piece"), QueryTriggerInteraction.Ignore))
            {
                AppendReceipt(prefix + "\"skipped\":\"lens_obstructed\",\"requested_lens\":" + JsonVector(shot.Lens.Value) + "}");
                if (shot.Fires) ReleaseHeldLight();
                yield break;
            }
            if (shot.Flash.HasValue)
            {
                DriveFlash(shot.Aim, shot.Lens.Value, shot.Flash.Value, FlashHoldSeconds);
                yield return new WaitForSeconds(.2f);
            }
            yield return new WaitForEndOfFrame();
            var file = $"{shot.ClusterId:0000}_{shot.Name}.png";
            try
            {
                var projection = CaptureProjection(shot, Path.Combine(directory, file), true);
                AppendReceipt(prefix + "\"file\":" + JsonString(file) + ",\"lens\":" + JsonVector(shot.Lens.Value)
                    + ",\"aim\":" + JsonVector(shot.Aim) + ",\"yaw\":" + JsonNumber(shot.Yaw)
                    + ",\"pitch\":" + JsonNumber(shot.Pitch) + ",\"fov\":" + JsonNumber(shot.VerticalFov.Value)
                    + ",\"occluded\":" + JsonBool(IsOccluded(shot.Lens.Value, shot.Aim)) + "," + projection + "}");
            }
            catch (Exception error)
            {
                AppendReceipt(prefix + "\"skipped\":" + JsonString("exact_capture_failed: " + error.Message) + "}");
                Logger.LogError(error);
            }
            finally { if (shot.Fires) ReleaseHeldLight(); }
        }

        // Render the actual game camera into a still-sized target; the desktop size is irrelevant.
        // All changes are synchronous and restored even when Render/ReadPixels/PNG encoding fails.
        private string CaptureProjection(Shot shot, string path, bool exact)
        {
            var camera = Camera.main;
            if (camera == null) throw new InvalidOperationException("game_camera_unavailable");
            var position = camera.transform.position;
            var rotation = camera.transform.rotation;
            var fov = camera.fieldOfView;
            var aspect = camera.aspect;
            var projection = camera.projectionMatrix;
            var rect = camera.rect;
            var orthographic = camera.orthographic;
            var target = camera.targetTexture;
            var active = RenderTexture.active;
            var post = camera.GetComponent<UnityEngine.PostProcessing.PostProcessingBehaviour>();
            var motionBlur = post?.profile?.motionBlur;
            var motionBlurEnabled = motionBlur != null && motionBlur.enabled;
            var width = shot.Width > 0 ? shot.Width : Screen.width;
            var height = shot.Height > 0 ? shot.Height : Screen.height;
            RenderTexture render = null;
            Texture2D image = null;
            string observed = null;
            byte[] png = null;
            try
            {
                if (exact) camera.transform.SetPositionAndRotation(shot.Lens.Value, Quaternion.Euler(shot.Pitch, shot.Yaw, shot.Roll));
                camera.orthographic = false;
                camera.fieldOfView = shot.VerticalFov ?? fov;
                camera.aspect = (float)width / height;
                camera.rect = new Rect(0, 0, 1, 1);
                camera.ResetProjectionMatrix();
                render = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
                render.Create();
                camera.targetTexture = render;
                // A still has no previous frame at this pose/projection. Reusing the
                // gameplay history creates false motion blur when FOV or roll changes.
                if (motionBlur != null) motionBlur.enabled = false;
                if (post != null) post.ResetTemporalEffects();
                camera.Render();
                var angles = camera.transform.eulerAngles;
                observed = "\"observed\":{\"lens\":[" + JsonNumber(camera.transform.position.x) + ","
                    + JsonNumber(camera.transform.position.y) + "," + JsonNumber(camera.transform.position.z)
                    + "],\"yaw\":" + JsonNumber(angles.y) + ",\"pitch\":" + JsonNumber(angles.x)
                    + ",\"roll\":" + JsonNumber(angles.z) + ",\"verticalFov\":" + JsonNumber(camera.fieldOfView)
                    + ",\"width\":" + render.width + ",\"height\":" + render.height + "}";
                RenderTexture.active = render;
                image = new Texture2D(width, height, TextureFormat.RGB24, false);
                image.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                image.Apply();
                png = image.EncodeToPNG();
                File.WriteAllBytes(path, png);
            }
            finally
            {
                camera.targetTexture = target;
                RenderTexture.active = active;
                camera.transform.SetPositionAndRotation(position, rotation);
                camera.orthographic = orthographic;
                camera.fieldOfView = fov;
                camera.aspect = aspect;
                camera.rect = rect;
                camera.projectionMatrix = projection;
                if (motionBlur != null) motionBlur.enabled = motionBlurEnabled;
                if (post != null) post.ResetTemporalEffects();
                if (image != null) Destroy(image);
                if (render != null) { render.Release(); Destroy(render); }
            }
            var restored = camera.targetTexture == target && camera.transform.position == position
                && Quaternion.Angle(camera.transform.rotation, rotation) < .001f
                && camera.fieldOfView == fov && camera.aspect == aspect && camera.rect == rect
                && camera.orthographic == orthographic && camera.projectionMatrix == projection
                && (motionBlur == null || motionBlur.enabled == motionBlurEnabled);
            using (var hash = SHA256.Create())
                return observed + ",\"temporal_history_reset\":" + JsonBool(post != null)
                    + ",\"camera_restored\":" + JsonBool(restored) + ",\"image_sha256\":"
                    + JsonString(BitConverter.ToString(hash.ComputeHash(png)).Replace("-", "").ToLowerInvariant());
        }
    }
}
