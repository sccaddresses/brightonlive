from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/"public_html"

def test_core_pages_exist():
    for name in ("index.html","map.html","calendar.html","travel.html","directory.html","community.html","contact.html","list-your-business.html","how-we-check.html"):
        assert (WEB/name).exists(), name

def test_local_refs_exist():
    errors=[]
    for html in WEB.glob("*.html"):
        text=html.read_text(encoding="utf-8")
        for ref in re.findall(r'(?:href|src)="([^"]+)"',text):
            if ref.startswith(("http://","https://","mailto:","tel:","#","javascript:")):
                continue
            clean=ref.split("?")[0].split("#")[0]
            if clean and not (WEB/clean).exists():
                errors.append((html.name,clean))
    assert not errors

def test_internal_review_data_not_in_webroot():
    names=[p.name.lower() for p in WEB.rglob("*") if p.is_file()]
    assert "review-queue.json" not in names
