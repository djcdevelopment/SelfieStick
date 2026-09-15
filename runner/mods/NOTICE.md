# Plugins in this kit

| file | version | license | source |
|---|---|---|---|
| `CameraProof.dll` | 0.3.1 (exact lens, vertical FOV, output dimensions, strict disposable save identity) | MIT | `github.com/djcdevelopment/SelfieStick`, `Plugin.cs` and `ExactCapture.cs`; built against the local Valheim client and BepInEx |
| `BetterServerPortals.dll` | 1.9.0 | GPL-3.0 | `github.com/redseiko`, commit `a2b4680`, `BetterServerPortals/`; not on Thunderstore for 1.0 at the time of this kit. Built against publicized Valheim 1.0 client assemblies: publicize `assembly_valheim.dll`/`assembly_utils.dll` with Mono.Cecil (or BepInEx.AssemblyPublicizer), lay them out as `<G>/valheim_server_Data/Managed/publicized_assemblies/`, then `dotnet build -p:GamePath=<G>` |

BetterServerPortals is redistributed here under the GPL-3.0 with this notice and the exact
commit it was built from; the full source is at the repository above. A prior 1.7.0
build does not load a 1.0 world (`MissingFieldException` in `ZDOMan.Load`); use the 1.9.0
build in this kit.

Verify before running:

    certutil -hashfile mods\CameraProof.dll SHA256
    certutil -hashfile mods\BetterServerPortals.dll SHA256

against the byte counts and SHA-256 in `runner-manifest.json`. The launcher verifies
every dependency before installing it. The pinned source transfer includes the
in-progress Baseline camera-kit changes; its provenance records that working snapshot.
