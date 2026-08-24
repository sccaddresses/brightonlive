from brightonlive.integrity import record_sha256, attach_integrity

def test_record_hash_is_deterministic():
    a={"name":"Example","category":"Cafe","updated_at":"x"}
    b={"category":"Cafe","name":"Example","updated_at":"y"}
    assert record_sha256(a) == record_sha256(b)

def test_attach_hash():
    r=attach_integrity({"name":"Example"})
    assert len(r["integrity_sha256"]) == 64
