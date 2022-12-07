import re
import random
import sys

import numpy as np
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from ontologies import WikiData
import csv

wikidata_dict = {
    "park": "Q22698",
    "public_garden": "Q55177716",
    "city_walls": "Q16748868",
    "church_building": "Q16970",
    "square": "Q174782",
    "cultural_event": "Q58687420",
    "museum":"Q33506",
    "monument":"Q4989906"
    #TODO Marco and Giacomo: add more items
}

def make_query(site_name, wikidata_id):
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

def parse_id(string):
    return string.split('http://www.wikidata.org/entity/')[1]

def wheelchair_friendly(v):
    return v['siteAccessibilityLabel'] == "\"wheelchair accessible\""
def init(filename):
    wikidata = WikiData()
    v_dict = {"site": parse_id}

    with open(filename, 'w+', encoding='utf8') as f_knowledge_base:
        for site_name, site_wikidata_id in wikidata_dict.items():
            q = make_query(site_name, site_wikidata_id)
            results = wikidata.query(q)

            results.function("label", "site", "siteLabel", v_dict=v_dict)
            results.function("position", "site", "siteLon", "siteLat",
                           k_dict={"siteLon": 'float', "siteLat": 'float'},
                           v_dict=v_dict)
            results.function("trip_advisor", "site", "siteTripAdvisorIdLabel",
                           k_dict={"siteTripAdvisorIdLabel": 'int'},
                           v_dict=v_dict)
            results.predicate("wheelchair_friendly", wheelchair_friendly,
                    "site", "siteAccessibilityLabel",
                    hidden=["siteAccessibilityLabel"],
                    v_dict=v_dict)
            f_knowledge_base.writelines(results.format_terms())

def main():
    init('KB_new.pl')

if __name__ == '__main__':
    main()
