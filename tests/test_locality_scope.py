from brightonlive.locality import in_public_scope, postcode_prefix

LOCATION={
    'core_postcode_prefixes':['BN1','BN2','BN3','BN41'],
    'latitude':50.8225,'longitude':-0.1372,'public_radius_km':9.0,
}

def test_postcode_scope_prefers_core_districts():
    assert postcode_prefix('bn3 1aa') == 'BN3'
    assert in_public_scope({'postcode':'BN3 1AA'}, LOCATION)
    assert not in_public_scope({'postcode':'BN7 2AA'}, LOCATION)

def test_coordinate_fallback_when_postcode_missing():
    assert in_public_scope({'latitude':50.8225,'longitude':-0.1372}, LOCATION)
    assert not in_public_scope({'latitude':50.873,'longitude':0.01}, LOCATION)
