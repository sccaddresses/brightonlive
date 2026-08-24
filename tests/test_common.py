from brightonlive.common import normalize_postcode, postcode_valid, domain_of, normalize_phone

def test_postcode_normalization():
    assert normalize_postcode("bn1 1aa") == "BN1 1AA"
    assert postcode_valid("BN1 1AA")

def test_domain_and_phone():
    assert domain_of("https://www.example.com/a") == "example.com"
    assert normalize_phone("+44 (0)1273 123456") in {"001273123456", "01273123456"}
