import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runner'))
import capture_spec as contract
import capture_kit


def specimen():
    return {'schema':contract.SCHEMA,'requiredPluginVersion':contract.PLUGIN_VERSION,
            'source':{'photoId':'era11-test','buildKey':'a'*64,'world':{'id':'ComfyEra11',
                'db':{'bytes':1,'sha256':'a'*64},'fwl':{'bytes':1,'sha256':'b'*64}}},
            'camera':{'lens':[123.45,90.25,-456.75],'yaw':90,'pitch':30,'roll':0,'verticalFov':65,'width':1920,'height':1080,'targetDistance':40},
            'settings':{'environment':'Clear','timeOfDay':.64,'fires':False,'flashBearing':None}}


class CaptureSpecTests(unittest.TestCase):
    def test_windows_save_directory_is_restored_on_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);active=root/'active';scratch=root/'scratch';active.mkdir();scratch.mkdir()
            (active/'original').write_bytes(b'original save');(scratch/'disposable').write_bytes(b'copied save')
            with self.assertRaisesRegex(RuntimeError,'capture failed'):
                with capture_kit.windows_save_root(scratch,active):
                    self.assertFalse((active/'original').exists());self.assertEqual(b'copied save',(active/'disposable').read_bytes())
                    (active/'disposable').write_bytes(b'game wrote here')
                    raise RuntimeError('capture failed')
            self.assertEqual(b'original save',(active/'original').read_bytes());self.assertFalse((active/'disposable').exists())
            self.assertEqual([],list(root.glob('active.selfiestick-*')))

    def test_windows_copy_failure_restores_original_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);active=root/'active';scratch=root/'scratch';active.mkdir();scratch.mkdir();(active/'original').write_bytes(b'keep')
            with patch.object(capture_kit.shutil,'copytree',side_effect=OSError('copy failed')):
                with self.assertRaises(OSError):
                    with capture_kit.windows_save_root(scratch,active):pass
            self.assertEqual(b'keep',(active/'original').read_bytes())

    def test_matrix_and_lens_feet_survive_runner(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'shots.tsv'
            for fov in (90,65,35):
                for frame in contract.FRAMES:
                    for size in (1920,3840):
                        s=specimen();w,h=contract.dimensions(frame,size);s['camera'].update(verticalFov=fov,width=w,height=h)
                        p.write_text(contract.shot_list(s));row=capture_kit.read_rows(p)[0]
                        self.assertEqual(23,len(row));self.assertEqual([123.45,90.25,-456.75],list(map(float,row[16:19])))
                        self.assertAlmostEqual(88.55,float(row[3]));self.assertEqual([fov,w,h],list(map(float,row[19:22])))
                        self.assertAlmostEqual(123.45+40*3**.5/2,float(row[9]));self.assertAlmostEqual(70.25,float(row[10]))

    def test_legacy_columns_preserved(self):
        path=Path(__file__).resolve().parents[1]/'runner/shots/shots-era11.tsv'
        rows=capture_kit.read_rows(path);self.assertGreater(len(rows),1);self.assertTrue(all(len(r)<=16 for r in rows))

    def test_bad_camera_and_plugin_fail(self):
        for key,value in [('verticalFov',float('nan')),('width',2000),('pitch',90),('lens',[1,float('inf'),3])]:
            s=specimen();s['camera'][key]=value
            with self.assertRaises(ValueError):contract.validate(s)
        s=specimen();s['requiredPluginVersion']='0.2.5'
        with self.assertRaisesRegex(ValueError,'incompatible'):contract.validate(s)

    def test_wrong_world_fails_before_capture(self):
        with tempfile.TemporaryDirectory() as d:
            db=Path(d)/'world.db';fwl=Path(d)/'world.fwl';db.write_bytes(b'archive');fwl.write_bytes(b'metadata')
            s=specimen();s['source']['world'].update(db=contract.file_record(db),fwl=contract.file_record(fwl))
            contract.verify_world(s,db,fwl);db.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'wrong archive'):contract.verify_world(s,db,fwl)

    def test_observed_must_match_and_restore(self):
        s=specimen();c=s['camera'];r={'plugin_version':contract.PLUGIN_VERSION,'exact':True,'observed':copy.deepcopy(c),'camera_restored':True}
        self.assertTrue(contract.verify_observed(s,r,[1920,1080]))
        for field,value in [('yaw',91),('verticalFov',64),('lens',[123.45,91.95,-456.75]),('height',720)]:
            changed=copy.deepcopy(r);changed['observed'][field]=value
            with self.assertRaises(ValueError):contract.verify_observed(s,changed,[1920,1080])
        r['camera_restored']=False
        with self.assertRaisesRegex(ValueError,'restoration'):contract.verify_observed(s,r,[1920,1080])


if __name__=='__main__':unittest.main()
