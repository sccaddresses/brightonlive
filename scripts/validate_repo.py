from pathlib import Path
import re, sys, json

ROOT=Path(__file__).resolve().parents[1]
errors=[]
required=[
 "README.md","pyproject.toml","config/brighton.yaml","config/directory-sources.yaml",
 "config/event-sources.yaml","public_html/index.html","public_html/map.html",
 "public_html/calendar.html","public_html/directory.html","src/brightonlive/pipeline.py",
]
for rel in required:
    if not (ROOT/rel).exists(): errors.append(f"missing required file: {rel}")

for html in (ROOT/"public_html").glob("*.html"):
    text=html.read_text(encoding="utf-8")
    if "<title>" not in text: errors.append(f"{html.name}: missing title")
    if 'name="viewport"' not in text: errors.append(f"{html.name}: missing viewport")
    if 'id="main"' not in text: errors.append(f"{html.name}: missing main")
    for ref in re.findall(r'(?:href|src)="([^"]+)"',text):
        if ref.startswith(("http://","https://","mailto:","tel:","#","javascript:")): continue
        clean=ref.split("?")[0].split("#")[0]
        if clean and not (ROOT/"public_html"/clean).exists():
            errors.append(f"{html.name}: missing local reference {clean}")

# The web root must not contain internal/review exports.
for bad in ("review-queue.json","internal","raw-source"):
    for p in (ROOT/"public_html").rglob("*"):
        if bad in p.name.lower():
            errors.append(f"web root contains internal/review material: {p.relative_to(ROOT)}")

if errors:
    print("\n".join(errors)); raise SystemExit(1)
print(f"PASS: repository/site validation ({len(list((ROOT/'public_html').glob('*.html')))} HTML pages)")
