from pathlib import Path
import yaml
from brightonlive.pipeline import run

def test_offline_fixture_pipeline(tmp_path, monkeypatch):
    root=Path(__file__).resolve().parents[1]
    cfg=yaml.safe_load((root/"config/brighton.yaml").read_text(encoding="utf-8"))
    cfg["outputs"]["directory"]=str(tmp_path/"exports")
    cfg["outputs"]["public_html_data"]=str(tmp_path/"webdata")
    cfg["directory"]["fixture_csv"]=str(root/"data/fixtures/listings.csv")
    cfg["events"]["fixture_csv"]=str(root/"data/fixtures/events.csv")
    config=tmp_path/"config.yaml"
    config.write_text(yaml.safe_dump(cfg,sort_keys=False),encoding="utf-8")

    result=run(str(config),offline=True,fixtures=True)
    assert result["directory"]["public_count"] == 2
    assert result["events"]["public_count"] == 2
    assert (tmp_path/"webdata/directory.v1.json").exists()
    assert (tmp_path/"webdata/events.v1.json").exists()
