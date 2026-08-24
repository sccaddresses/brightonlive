from brightonlive.directory.entity_resolution import same_entity, resolve

def test_same_domain_and_postcode_merges():
    a={"name":"Example Cafe","postcode":"BN1 1AA","website":"https://example.com","evidence":[]}
    b={"name":"Example Café","postcode":"BN1 1AA","website":"https://www.example.com/menu","evidence":[]}
    assert same_entity(a,b)
    assert len(resolve([a,b])) == 1

def test_different_branch_postcodes_do_not_merge_by_domain():
    a={"name":"Chain","postcode":"BN1 1AA","website":"https://chain.example","evidence":[]}
    b={"name":"Chain","postcode":"BN3 2BB","website":"https://chain.example","evidence":[]}
    assert not same_entity(a,b)
