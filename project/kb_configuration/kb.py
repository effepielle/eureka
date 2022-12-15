import random
from functools import partial
from ontologies import WikiData, DatiCultura

wikidata_dict = {
    "park": "Q22698",
    "public_garden": "Q55177716",
    "city_walls": "Q16748868",
    "church_building": "Q16970",
    "square": "Q174782",
    "cultural_event": "Q58687420",
    "museum":"Q33506",
    "monument":"Q4989906",
    "library": "Q7075",
    "tower": "Q12518",
    "city_gate": "Q82117",
    "bridge": "Q12280",
    "palace": "Q16560",
    "cemetery": "Q39614",
    "theater": "Q24354",
    "arts_venue": "Q15090615"
}

def wikidata_make_query(wikidata_id):
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

def daticultura_make_query():
    return """
    prefix city: <http://dati.beniculturali.it/mibact/luoghi/resource/City/>
    SELECT DISTINCT
    (?Id as ?Wikidata_id)
    ?Orari_di_apertura 
    (str(?Biglietti) as ?costo_biglietti)

    WHERE {
        ?Risorsa  a cis:CulturalInstituteOrSite.
        MINUS
        {?Risorsa  a cis:CultResearchCenter.}
        ?Risorsa  cis:institutionalCISName ?Nome_Istituzionale; 
            cis:hasSite/cis:siteAddress/clvapit:hasCity city:Pisa.
        optional {?Risorsa  accessCondition:hasAccessCondition [a accessCondition:OpeningHoursSpecification ;
                                                        l0:description ?Orari_di_apertura ]. }
        optional {
        ?Risorsa potapit:hasTicket ?ticket .
        ?offer potapit:includes ?ticket ;
                potapit:hasPriceSpecification [potapit:hasCurrencyValue ?Biglietti]. }
    ?Risorsa owl:sameAs ?Id.
    FILTER regex(?Id, "^http://www.wikidata.org/entity/")
        }
    """

def parse_id(string):
    return string.split('http://www.wikidata.org/entity/')[1]

def wheelchair_friendly(v):
    return v['siteAccessibilityLabel'] == "\"wheelchair accessible\""

def is_free(v):
    return v['costo_biglietti'] == "\"Gratuito\""


def init(filename, rules_file=None):
    wikidata = WikiData()
    daticultura = DatiCultura()
    v_dict = {"site": parse_id, "Wikidata_id": parse_id}
    predicates = set()
    ids = set()

    with open(filename, 'w+', encoding='utf8') as f_knowledge_base:
        if rules_file:
            f_knowledge_base.write(f":-include(\"{rules_file}\").\n\n")

        for site_name, site_wikidata_id in wikidata_dict.items():
            q = wikidata_make_query(site_wikidata_id)
            results = wikidata.query(q)

            # Site label predicates
            results.predicate("label", "site", "siteLabel", v_dict=v_dict) \
                    .build()

            # Site geoposition predicates
            results.predicate("position", "site", "siteLon", "siteLat",
                    k_dict={"siteLon": 'float', "siteLat": 'float'},
                    v_dict=v_dict) \
                            .unique("site") \
                            .build()

            # Site tripadvisor id predicates
            results.predicate("trip_advisor", "site", "siteTripAdvisorIdLabel",
                    k_dict={"siteTripAdvisorIdLabel": 'int'},
                    v_dict=v_dict) \
                            .build()

            # Site (random) rating predicates
            results.predicate("star", "site", v_dict=v_dict) \
                    .closure("stars", partial(random.randrange, 6)) \
                    .filter(lambda v: v["site"] not in ids) \
                    .unique("site") \
                    .build()

            # Site type predicates
            results.predicate("type", "site", v_dict=v_dict) \
                    .constant("site_class", site_name) \
                    .build()

            # Site image predicates
            results.predicate("image", "site", "siteImage", v_dict=v_dict) \
                    .build()

            # Site wheelchair accessibility predicates
            results.predicate("wheelchair_friendly", "site",
                    "siteAccessibilityLabel", v_dict=v_dict) \
                            .filter(wheelchair_friendly) \
                            .project("site") \
                            .build()

            ids.update([p.get('site') for p in results.get_predicates()])
            predicates.update(results.format_predicates())

        q = daticultura_make_query()
        results = daticultura.query(q)

        results.predicate("pricing_information", "Wikidata_id", "costo_biglietti",
                v_dict=v_dict) \
                .project("Wikidata_id", "costo_biglietti") \
                .build()

        predicates.update(results.format_predicates())

        f_knowledge_base.writelines(sorted(predicates))

def main():
    init('KB_new.pl', rules_file='rules.pl')

if __name__ == '__main__':
    main()
