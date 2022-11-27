from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")

# WikiData Item Name - WikiData Item ID
dict = {
    "park": "Q22698",
    "public_garden": "Q55177716",
    "city_walls": "Q16748868",
    "church_building": "Q16970"
    #TODO: add more items
}

for site_name, site_wikidata_id in dict.items():
    if site_name == "city_walls":
        sparql.setQuery("""
    SELECT ?site ?siteLabel ?siteAccessibilityLabel ?siteTripAdvisorIdLabel ?siteImage{
    {
    SELECT DISTINCT ?site ?siteLabel ?siteAccessibilityLabel ?siteTripAdvisorIdLabel ?siteImage
    WHERE
    {       
    ?site wdt:P131 wd:Q13375;
            wdt:P31/wdt:P279* wd:""" + site_wikidata_id + """;
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

        #hard coded coordinates of city walls from Piazza dei Miracoli (source: Google Maps)
        for index, row in results_df.iterrows():
            predicate_string = "{}({}, {}, {}, {} ".format(site_name, row["site.value"].split('http://www.wikidata.org/entity/')[1], row["siteLabel.value"], "43.72518845930142", "43.72518845930142") 
            
            if 'siteAccessibilityLabel.value' in results_df:
                predicate_string += "{}, ".format(row["siteAccessibilityLabel.value"])
            if 'siteTripAdvisorId.value' in results_df:
                predicate_string += "{}, ".format(row["siteTripAdvisorId.value"])
            if 'siteImage.value' in results_df:
                predicate_string += "{}".format(row["siteImage.value"])
            predicate_string += ").\n"

    else:
        #TODO: define a function
        sparql.setQuery("""
    SELECT ?site ?siteLabel ?siteLat ?siteLon ?siteAccessibilityLabel ?siteTripAdvisorIdLabel ?siteImage{
    {
    SELECT DISTINCT ?site ?siteLabel ?siteLat ?siteLon ?siteAccessibilityLabel ?siteTripAdvisorIdLabel ?siteImage
    WHERE
    {       
    ?site wdt:P131 wd:Q13375;
            wdt:P31/wdt:P279* wd:""" + site_wikidata_id + """;
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

        for index, row in results_df.iterrows():
            predicate_string = "{}({}, {}, {}, {}, ".format(site_name, row["site.value"].split('http://www.wikidata.org/entity/')[1], row["siteLabel.value"], row["siteLat.value"], row["siteLon.value"])
            if 'siteAccessibilityLabel.value' in results_df:
                predicate_string += "{}, ".format(row["siteAccessibilityLabel.value"])
            if 'siteTripAdvisorId.value' in results_df:
                predicate_string += "{}, ".format(row["siteTripAdvisorId.value"])
            if 'siteImage.value' in results_df:
                predicate_string += "{}".format(row["siteImage.value"])
            predicate_string += ").\n"

#TODO: save items into a KB file


