#!/usr/bin/env python3
"""Build an immutable local runner candidate; publication and capture proof are separate."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import zipfile
from capture_spec import PLUGIN_VERSION, file_record

HERE = Path(__file__).resolve().parent
FILES = ['capture.py','capture_kit.py','capture_spec.py','Capture.ps1','capture.sh','README.md',
         'Invoke-EraCapture.ps1','mods/NOTICE.md']


def build(output, camera_dll, portal_dll):
    output.mkdir(parents=True, exist_ok=False)
    root=output/'runner';root.mkdir()
    for name in FILES:
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(HERE/name,target)
    for name,source in [('CameraProof.dll',camera_dll),('BetterServerPortals.dll',portal_dll)]:
        shutil.copy2(source,root/'mods'/name)
    files=[{'path':p.relative_to(root).as_posix(),**file_record(p)} for p in sorted(root.rglob('*')) if p.is_file()]
    manifest={'schema':'selfiestick-runner/v1','pluginVersion':PLUGIN_VERSION,
              'sourceRevision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
              'candidate':True,'files':files}
    (root/'runner-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    package=output/f'selfiestick-runner-{PLUGIN_VERSION}.zip'
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(root).as_posix())
    release={'schema':'selfiestick-runner-release/v1','pluginVersion':PLUGIN_VERSION,
             'sourceRevision':manifest['sourceRevision'],'candidate':True,
             'package':{'path':package.name,**file_record(package)}}
    (output/'release.json').write_text(json.dumps(release,indent=2)+'\n',encoding='utf-8')
    return release


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--camera-dll',type=Path,required=True)
    p.add_argument('--portal-dll',type=Path,required=True)
    args=p.parse_args();print(json.dumps(build(args.out,args.camera_dll,args.portal_dll),indent=2))
