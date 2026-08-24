from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/"dist"; out.mkdir(exist_ok=True)
path=out/"brightonlive-public_html.zip"
with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
    for p in (ROOT/"public_html").rglob("*"):
        if p.is_file(): z.write(p,Path("public_html")/p.relative_to(ROOT/"public_html"))
print(path)
