import re
import random
import sys

import numpy as np
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

# agent to use sparql endpoint
user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql", agent=user_agent)

def main():
    # WikiData Item Name - WikiData Item ID
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

    for site_name, site_wikidata_id in wikidata_dict.items():
        if site_name == "city_walls":
            compute_hard_coded_address_query(site_name,site_wikidata_id,
                                                    43.72518845930142, 10.39367112698515)
            #TODO Francesco: insert np.nan or coordinate of the cultural event
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

    with open("KB.pl", 'a+', encoding='utf8') as f_knowledge_base:
        for _, row in results_df.iterrows():

            predicate_string = (
                                    f"{site_name}"
                                    f"(\"{(row['site.value'].split('http://www.wikidata.org/entity/')[1])}\", "
                                    f"\"{row['siteLabel.value']}\", "
                                    f"{row['siteLat.value']}, "
                                    f"{row['siteLon.value']}, "
            )

            if 'siteAccessibilityLabel.value' in results_df:
                if pd.notna(row["siteAccessibilityLabel.value"]):
                    predicate_string += f"\"{row['siteAccessibilityLabel.value']}\", "
                else:
                    predicate_string += f"{row['siteAccessibilityLabel.value']}, "
            else:
                predicate_string += f"{np.nan}, "
            if 'siteTripAdvisorIdLabel.value' in results_df:
                predicate_string += f"{row['siteTripAdvisorIdLabel.value']}, "
            else:
                predicate_string += f"{np.nan}, "
            if 'siteImage.value' in results_df:
                if pd.notna(row["siteImage.value"]):
                    predicate_string += f"\"{row['siteImage.value']}\","
                else:
                    predicate_string += f"{row['siteImage.value']},"
            else:
                predicate_string += f"{np.nan}, "

            #random generated star
            predicate_string += f"{random.randrange(6)}"
            predicate_string += ").\n"
            predicate_string = re.sub(",+\)\.",").",predicate_string)
            f_knowledge_base.write(predicate_string)

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

    with open("KB.pl", 'a+', encoding='utf8') as f_knowledge_base:
        for _, row in results_df.iterrows():
            # hard-coded coordinates of city walls entrance
            # from Piazza dei Miracoli (source: Google Maps)
            predicate_string = (
                f"{site_name}"
                f"(\"{row['site.value'].split('http://www.wikidata.org/entity/')[1]}\", "
                f"\"{row['siteLabel.value']}\", "
                f"{lat}"
                f"{lon}, "
            )

            if 'siteAccessibilityLabel.value' in results_df:
                if pd.notna(row['siteAccessibilityLabel.value']):
                    predicate_string += f"\"{row['siteAccessibilityLabel.value']}\", "
                else:
                    predicate_string += f"{row['siteAccessibilityLabel.value']}, "
            else:
                predicate_string += f"{np.nan}, "
            if 'siteTripAdvisorIdLabel.value' in results_df:
                predicate_string += f"{row['siteTripAdvisorIdLabel.value']}, "
            else:
                predicate_string += f"{np.nan}, "
            if 'siteImage.value' in results_df:
                if pd.notna(row['siteImage.value']):
                    predicate_string += f"\"{row['siteImage.value']}\",".format()
                else:
                    predicate_string += f"{row['siteImage.value']},"
            else:
                predicate_string += f"{np.nan}, "

            # random generated star
            predicate_string += f"{random.randrange(6)}"

            predicate_string += ").\n"
            predicate_string = re.sub(",+\)\.", ").", predicate_string)
            f_knowledge_base.write(predicate_string)

if __name__ == '__main__':
    main()
