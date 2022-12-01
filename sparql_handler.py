import re
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import sys

#agent to use sparql endpoint
user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql", agent=user_agent)

def main():
    # WikiData Item Name - WikiData Item ID
    dict = {
        "park": "Q22698",
        "public_garden": "Q55177716",
        "city_walls": "Q16748868",
        "church_building": "Q16970",
        "square": "Q174782",
        #TODO: event may not have coordinates, what we need to do?
        "cultural_event": "Q58687420",
        "museum":"Q33506",
        "monument":"Q4989906"
        #TODO: add more items
    }

    for site_name, site_wikidata_id in dict.items():
        if site_name == "city_walls":
            compute_hard_coded_address_query(site_name,site_wikidata_id, 43.72518845930142, 10.39367112698515)
        else:
            compute_query(site_name,site_wikidata_id)


def compute_query(site_name,wikidata_id):
    sparql.setQuery("""
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
    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    results_df = pd.json_normalize(results['results']['bindings'])

    f = open("KB.pl", 'a+')
    for index, row in results_df.iterrows():
        predicate_string = "{}(\"{}\", \"{}\", {}, {}, ".format(site_name,
                                                        row["site.value"].split('http://www.wikidata.org/entity/')[1],
                                                        row["siteLabel.value"], row["siteLat.value"],
                                                        row["siteLon.value"])
        if 'siteAccessibilityLabel.value' in results_df and pd.notna(row["siteAccessibilityLabel.value"]):
            predicate_string += "\"{}\", ".format(row["siteAccessibilityLabel.value"])
        if 'siteTripAdvisorId.value' in results_df and pd.notna(["siteTripAdvisorId.value"]):
            predicate_string += "{}, ".format(row["siteTripAdvisorId.value"])
        if 'siteImage.value' in results_df and pd.notna(row['siteImage.value']):
            predicate_string += "\"{}\"".format(row["siteImage.value"])
        predicate_string += ").\n"
        predicate_string = re.sub(",\s*\)\.", ").", predicate_string)
        f.write(predicate_string)
    f.close()

def compute_hard_coded_address_query(site_name,wikidata_id, lat, lon):
    sparql.setQuery("""
        SELECT ?site ?siteLabel ?siteAccessibilityLabel ?siteTripAdvisorIdLabel ?siteImage{
        {
        SELECT DISTINCT ?site ?siteLabel ?siteAccessibilityLabel ?siteTripAdvisorIdLabel ?siteImage
        WHERE
        {       
        ?site wdt:P131 wd:Q13375;
                wdt:P31/wdt:P279* wd:""" + wikidata_id + """;
        OPTIONAL {?site wdt:P2846 ?siteAccessibility.}
        OPTIONAL {?site wdt:P3134 ?siteTripAdvisorId.}
        OPTIONAL {?site wdt:P18 ?siteImage.}

        SERVICE wikibase:label { bd:serviceParam wikibase:language "en"}.
        }
        }
        FILTER (!REGEX(?siteLabel, "^Q[0-9]+$"))
        }
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    results_df = pd.json_normalize(results['results']['bindings'])

    f = open("KB.pl", 'a+')
    for index, row in results_df.iterrows():
        # hard-coded coordinates of city walls entrance from Piazza dei Miracoli (source: Google Maps)
        predicate_string = "{}(\"{}\", \"{}\", {}, {}, ".format(site_name,
                                                       row["site.value"].split('http://www.wikidata.org/entity/')[1],
                                                       row["siteLabel.value"], lat, lon)

        if 'siteAccessibilityLabel.value' in results_df and pd.notna(row["siteAccessibilityLabel.value"]):
            predicate_string += "\"{}\", ".format(row["siteAccessibilityLabel.value"])
        if 'siteTripAdvisorId.value' in results_df and pd.notna(["siteTripAdvisorId.value"]):
            predicate_string += "{}, ".format(row["siteTripAdvisorId.value"])
        if 'siteImage.value' in results_df and pd.notna(row['siteImage.value']):
            predicate_string += "\"{}\"".format(row["siteImage.value"])
        predicate_string += ").\n"
        predicate_string = re.sub(",+\)\.",").",predicate_string)
        f.write(predicate_string)
    f.close()

if __name__ == '__main__':
    main()
