import random
from functools import partial
from locale import atof, setlocale, LC_NUMERIC
from ontologies import WikiData, DatiCultura


wikidata_dict = {
    "park": "Q22698",
    "public_garden": "Q55177716",
    "city_walls": "Q16748868",
    "church_building": "Q16970",
    "square": "Q174782",
    "museum": "Q33506",
    "monument": "Q4989906",
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
    """ Make a query to WikiData according to the wikidata_id of the asset type to retrieve.

    Args:
        wikidata_id: the wikidata_id of the asset type to retrieve

    Returns:
        str: the query string to execute
    """

    # city_walls don't have position so we need to retrieve them separately
    if wikidata_id == "Q16748868":
        return """
        SELECT ?site ?siteLabel ?siteLat ?siteLon ?siteAccessibilityLabel ?siteTripAdvisorIdLabel ?siteImage{
        {
        SELECT DISTINCT ?site ?siteLabel ?siteLat ?siteLon ?siteAccessibilityLabel ?siteTripAdvisorIdLabel ?siteImage
        WHERE
        {       
        ?site wdt:P131 wd:Q13375;
                wdt:P31/wdt:P279* wd:""" + wikidata_id + """.
        OPTIONAL {
                  ?site p:P625 ?siteCoordinates.
                  ?siteCoordinates psv:P625 ?coordinate_node.
                  ?coordinate_node wikibase:geoLongitude ?siteLon;
                                   wikibase:geoLatitude ?siteLat.
                 }
        OPTIONAL {?site wdt:P2846 ?siteAccessibility.}
        OPTIONAL {?site wdt:P3134 ?siteTripAdvisorId.}
        OPTIONAL {?site wdt:P18 ?siteImage.}
    
        
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en"}.
        }
        }
        FILTER (!REGEX(?siteLabel, "^Q[0-9]+$"))
        } ORDER BY DESC(?siteLabel) LIMIT 1
        """
    else:
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
    """ Make a query to DatiCultura to retrieve additional information about the assets.

    Returns:
        str: the query string to execute 
    """
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
    """ Parse the wikidata_id from the wikidata url.

    Args:
        string: the wikidata url

    Returns:
        str: the wikidata_id
    """
    return string.split('http://www.wikidata.org/entity/')[1]


def wheelchair_friendly(v):
    """ Check if the asset is wheelchair friendly. 
    Args:
        v: the asset to check

    Returns:
        bool: True if the asset is wheelchair friendly, False otherwise
    """
    return v['siteAccessibilityLabel'] == "\"wheelchair accessible\""


def valid_timetable_entry(v):
    """ Check if the asset has a valid timetable entry.

    Args:
        v: the asset to check

    Returns:
        bool: True if the asset has a valid timetable entry, False otherwise
    """    
    return "(" in v['Orari_di_apertura'] and ")" in v["Orari_di_apertura"]


def recover_opening_time(day, v, index=-1):
    """ Recover the opening time of the asset for a specific day.

    Args:
        day: the day of the week
        v: the asset
        index: the index of the opening time to recover. Defaults to -1.
    """
    def recover_day_opening_time(string, day, index=-1):
        """

        Args:
            string (_type_): _description_
            day (_type_): _description_
            index (int, optional): _description_. Defaults to -1.

        Returns:
            _type_: _description_
        """        
        s = string.split(day)[1].split("|")[0]
        if "/" not in s:
            return f'{s.split(",")[0]}'
        elif index == 0:
            return f'{s.split("/")[0]}'
        elif index == 1:
            return f'{s.split(",")[1].split("/")[0]}'
        else:
            return f'{s.split("/")[0]} {s.split(",")[1].split("/")[0]}'

    def recover_undefined(string):
        return None

    tmp = v.lower().replace(":", ".")
    if day == "lun":
        return recover_day_opening_time(tmp, " (", index)
    elif day == "mar":
        return recover_day_opening_time(tmp, "martedi (", index)
    elif day == "mer":
        return recover_day_opening_time(tmp, "mercoledi (", index)
    elif day == "gio":
        return recover_day_opening_time(tmp, "giovedi (", index)
    elif day == "ven":
        return recover_day_opening_time(tmp, "venerdi (", index)
    elif day == "sab":
        return recover_day_opening_time(tmp, "sabato (", index)
    elif day == "dom":
        return recover_day_opening_time(tmp, "domenica (", index)
    else:
        return recover_undefined(tmp)


def recover_closing_time(day, v, index=-1):
    """ Recover the closing time of the asset for a specific day.

    Args:
        day: the day of the week
        v: the asset
        index (int, optional): the index of the closing time to recover. Defaults to -1.
    """
    def recover_day_closing_time(string, day, index=-1):
        s = string.split(day)[1].split("|")[0].replace(")", "")
        if "/" not in s:
            return f'{s.split(",")[1]}'
        elif index == 0:
            return f'{s.split("/")[1].split(",")[0]}'
        elif index == 1:
            return f'{s.split(",")[1].split("/")[1]}'
        else:
            return f'{s.split("/")[1].split(",")[0]} {s.split(",")[1].split("/")[1]}'

    def recover_undefined(string):
        return None

    tmp = v.lower().replace(":", ".").replace('"', "")
    if day == "lun":
        return recover_day_closing_time(tmp, " (", index)
    elif day == "mar":
        return recover_day_closing_time(tmp, "martedi (", index)
    elif day == "mer":
        return recover_day_closing_time(tmp, "mercoledi (", index)
    elif day == "gio":
        return recover_day_closing_time(tmp, "giovedi (", index)
    elif day == "ven":
        return recover_day_closing_time(tmp, "venerdi (", index)
    elif day == "sab":
        return recover_day_closing_time(tmp, "sabato (", index)
    elif day == "dom":
        return recover_day_closing_time(tmp, "domenica (", index)
    else:
        return recover_undefined(tmp)


def init(filename, rules_file=None):
    """ Build facts from ontology retrieved data and write them in the knowledge base file.

    Args:
        filename: the knowledge base file 
        rules_file: the rules file to include in the knowledge base file
    """
    wikidata = WikiData()
    daticultura = DatiCultura()
    v_dict = {"site": parse_id, "Wikidata_id": parse_id}
    predicates = set()
    ids = set()
    days_dict = {
        "lun": "monday",
        "mar": "tuesday",
        "mer": "wednesday",
        "gio": "thursday",
        "ven": "friday",
        "sab": "saturday",
        "dom": "sunday"
    }
    setlocale(LC_NUMERIC, '') 

    with open(filename, 'w+', encoding='utf8') as f_knowledge_base:
        if rules_file:
            f_knowledge_base.write(f":-include(\"{rules_file}\").\n\n")

        for site_name, site_wikidata_id in wikidata_dict.items():
            q = wikidata_make_query(site_wikidata_id)
            results = wikidata.query(q)
            
            # city walls doesn't have coordinates, added coordinate of main entrance
            if site_wikidata_id == "Q16748868":
                results.df["siteLat.type"] = 'literal'
                results.df["siteLat.value"] = "43.72452940120137"
                results.df["siteLon.type"] = 'literal'
                results.df["siteLon.value"] = '10.393724768399192'

            # site label predicates
            results.predicate("label", "site", "siteLabel", v_dict=v_dict) \
                .build()

            # site geoposition predicates
            results.predicate("position", "site", "siteLat", "siteLon",
                              k_dict={"siteLon": 'float', "siteLat": 'float'},
                              v_dict=v_dict) \
                .unique("site") \
                .build()

            # site tripadvisor id predicates
            results.predicate("trip_advisor", "site", "siteTripAdvisorIdLabel",
                              k_dict={"siteTripAdvisorIdLabel": 'int'},
                              v_dict=v_dict) \
                .build()

            # site (random) rating predicates
            results.predicate("star", "site", v_dict=v_dict) \
                .closure("stars", partial(random.randrange, 1, 6)) \
                .filter(lambda v: v["site"] not in ids) \
                .unique("site") \
                .build()

            # site type predicates
            results.predicate("type", "site", v_dict=v_dict) \
                .constant("site_class", site_name) \
                .build()

            # site image predicates
            results.predicate("image", "site", "siteImage", v_dict=v_dict) \
                .build()

            # site wheelchair accessibility predicates
            results.predicate("wheelchair_friendly", "site",
                              "siteAccessibilityLabel", v_dict=v_dict) \
                .filter(wheelchair_friendly) \
                .project("site") \
                .build()

            ids.update([p.get('site') for p in results.get_predicates()])
            predicates.update(results.format_predicates())

        q = daticultura_make_query()
        results = daticultura.query(q)

        # ticket cost predicates
        results.predicate("ticket_cost", "Wikidata_id", "costo_biglietti",
                          v_dict=v_dict) \
            .map("costo_biglietti", lambda v: float(0) if "Gratuito" in v else atof(v.replace('"', ""))) \
            .project("Wikidata_id", "costo_biglietti") \
            .build()

        for day, translation in days_dict.items():
            results.predicate("timetable_info", "Wikidata_id", "Orari_di_apertura",
                              v_dict=v_dict) \
                .filter(valid_timetable_entry) \
                .compute("Orari_di_apertura", "day", lambda v: translation if day in v.lower() else None) \
                .compute("Orari_di_apertura", "opening_time", lambda v: recover_opening_time(day, v, 0)) \
                .map("opening_time", lambda v: float(v.strip("0").replace('"', ""))) \
                .compute("Orari_di_apertura", "closing_time", lambda v: recover_closing_time(day, v, 0)) \
                .map("closing_time", lambda v: float(v.strip("0").replace('"', ""))) \
                .project("Wikidata_id", "day", "opening_time", "closing_time") \
                .build()
            results.predicate("timetable_info", "Wikidata_id", "Orari_di_apertura",
                              v_dict=v_dict) \
                .filter(valid_timetable_entry) \
                .compute("Orari_di_apertura", "day", lambda v: translation if day in v.lower() else None) \
                .compute("Orari_di_apertura", "opening_time", lambda v: recover_opening_time(day, v, 1)) \
                .map("opening_time", lambda v: float(v.strip("0").replace('"', ""))) \
                .compute("Orari_di_apertura", "closing_time", lambda v: recover_closing_time(day, v, 1)) \
                .map("closing_time", lambda v: float(v.strip("0").replace('"', ""))) \
                .project("Wikidata_id", "day", "opening_time", "closing_time") \
                .build()

        predicates.update(results.format_predicates())

        f_knowledge_base.writelines(sorted(predicates))


def main():
    init('KB.pl', rules_file='rules.pl')


if __name__ == '__main__':
    main()
