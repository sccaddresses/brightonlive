from pathlib import Path
import hashlib, json
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
exclude={".git"}
rows=[]
for p in sorted(ROOT.rglob("*")):
    if not p.is_file(): continue
    if any(part in exclude or part==".venv" for part in p.parts): continue
    rel=p.relative_to(ROOT).as_posix()
    if rel in {"MANIFEST.json","SHA256SUMS.txt"}: continue
    rows.append({"path":rel,"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
manifest={"generated_at":datetime.now(timezone.utc).isoformat(),"algorithm":"SHA-256","files":rows}
(ROOT/"MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
(ROOT/"SHA256SUMS.txt").write_text("".join(f"{r['sha256']}  {r['path']}\n" for r in rows),encoding="utf-8")
print("manifest files:",len(rows))
