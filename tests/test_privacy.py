from brightonlive.privacy import public_directory_record

def test_suppressed_address_and_contact_removed():
    r={
      "name":"Home service","address":"1 Home Road","postcode":"BN1 1AA","latitude":50.8,"longitude":-0.1,
      "phone":"01273","email":"x@example.com",
      "address_public":False,"phone_public":False,"email_public":False,
      "evidence":[{"source_owner":"Source","source_url":"https://example.com","source_type":"owned_primary","retrieved_at":"2026-08-23"}],
      "review_notes":"private"
    }
    out=public_directory_record(r)
    for key in ("address","postcode","latitude","longitude","phone","email","review_notes"):
        assert key not in out
