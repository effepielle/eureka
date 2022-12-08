import numpy as np
import pandas as pd
from ontologies import WikiData, Result
from functools import partial
import random

def compute_query(site_name, wikidata_id):
    return """
    SELECT ?site ?siteLabel ?siteLat ?siteLon ?siteAccessibilityLabel ?siteTripAdvisorIdLabel ?siteImage{
    {
    SELECT DISTINCT ?site ?siteLabel ?siteLat ?siteLon ?siteAccessibilityLabel ?siteTripAdvisorIdLabel ?siteImage
    WHERE
    {       
    ?site wdt:P131 wd:Q13375;
            wdt:P31/wdt:P279* wd:""" + wikidata_id + """;
            p:P625 ?siteCoordinates;
    OPTIONAL {?site wdt:P2846 ?siteAccessibility.}
    OPTIONAL {?site wdt:P3134 ?siteTripAdvisorId.}
    OPTIONAL {?site wdt:P18 ?siteImage.}

    ?siteCoordinates psv:P625 ?coordinate_node.
    ?coordinate_node wikibase:geoLongitude ?siteLon.
    ?coordinate_node wikibase:geoLatitude ?siteLat.
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en"}.
    }
    }
    FILTER (!REGEX(?siteLabel, "^Q[0-9]+$"))
    }
    """

def test_ontologies(verbose=False):
    wikidata = WikiData()
    q = compute_query("church_building", "Q16970")

    results = wikidata.query(q)
    d = {"siteTripAdvisorIdLabel": 'int', "siteLon": 'float' }
    v_dict = {"site": lambda v: v.split('http://www.wikidata.org/entity/')[1]}

    results.predicate("tuple", "site", "siteLabel", "siteAccessibilityLabel", k_dict=d, v_dict=v_dict) \
            .build()

    kb = [str(term) for term in results.terms]

    if verbose:
        print('\n'.join(kb))

    assert results
    assert kb
    assert any("\"wheelchair accessible\"" in term for term in kb)

# TODO
def test_predicate_filters(verbose=False):
    wikidata = WikiData()
    q = compute_query("church_building", "Q16970")

    results = wikidata.query(q)
    v_dict = {"site": lambda v: v.split('http://www.wikidata.org/entity/')[1]}
    f = lambda v: v['siteAccessibilityLabel'] == "\"wheelchair accessible\""
    results.predicate("wheelchair_friendly", "site", "siteAccessibilityLabel", v_dict=v_dict) \
            .filter(f) \
            .project("site") \
            .build()

    kb = [str(term) for term in results.terms]
    if verbose:
        print('\n'.join(kb))

    assert results
    assert kb
    assert any("wheelchair_friendly" in term for term in kb)


def test_predicate_constants(verbose=False):
    wikidata = WikiData()
    q = compute_query("church_building", "Q16970")

    results = wikidata.query(q)
    v_dict = {"site": lambda v: v.split('http://www.wikidata.org/entity/')[1]}

    results.predicate("type", "site", v_dict=v_dict) \
            .constant("class", "church_building") \
            .build()

    kb = [str(term) for term in results.terms]

    if verbose:
        print('\n'.join(kb))

    assert results
    assert kb
    assert any("\"church_building\"" in term for term in kb)

def test_predicate_closures(verbose=False):
    wikidata = WikiData()
    q = compute_query("church_building", "Q16970")

    results = wikidata.query(q)
    v_dict = {"site": lambda v: v.split('http://www.wikidata.org/entity/')[1]}

    results.predicate("star", "site", v_dict=v_dict) \
            .closure("stars", partial(random.randrange, 6)) \
            .build()

    kb = [str(term) for term in results.terms]

    if verbose:
        print('\n'.join(kb))

    assert results
    assert kb
    assert any("star" in term for term in kb)
    stars = [term.get("stars") for term in results.terms] 
    assert not(stars.count(stars[0]) == len(stars))



if __name__ == '__main__':
    test_ontologies(verbose=True)
    test_predicate_filters(verbose=True)
    test_predicate_constants(verbose=True)
    test_predicate_closures(verbose=True)
    print('Tests passed')
