from pathlib import Path
import shutil, zipfile, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
subprocess.check_call([sys.executable,str(ROOT/"scripts/validate_repo.py")])
subprocess.check_call([sys.executable,str(ROOT/"scripts/generate_integrity_manifest.py")])

dist=ROOT/"dist"; dist.mkdir(exist_ok=True)
zip_path=dist/"brightonlive-repository.zip"
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
    for p in ROOT.rglob("*"):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if rel.parts and rel.parts[0] in {".venv","dist","exports"}: continue
        z.write(p,Path("BrightonLive")/rel)
print(zip_path)
