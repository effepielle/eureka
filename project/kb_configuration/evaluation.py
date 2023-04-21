from unittest import result
import time
from kb import wikidata_make_query, wikidata_dict
from ontologies import WikiData
from swiplserver import PrologMQI

# This file contains simple functions to automatcally query wikidata and prolog knowledge base and calculate the average time of the query


def wikidata_query_time_evaluation(wikidata_id, upper_range):
    """Query wikidata and calculate the average time of the query

    Args:
        wikidata_id: wikidara id of the asset
        upper_range: number of times to repeat the query

    Returns:
        float: average time of the query
    """
    time_list = []
    for i in range(upper_range):
        wikidata_obj = WikiData()
        start = time.time()
        wikidata_obj.query(wikidata_make_query(wikidata_id))
        end = time.time()
        time_list.append(end - start)
    return sum(time_list)/len(time_list)


def knowledge_base_time_evaluation(asset_type, upper_range):
    """Query prolog knowledge base and calculate the average time of the query

    Args:
        asset_type: type of the asset (its label in the knowledge base)
        upper_range: number of times to repeat the query

    Returns:
            float: average time of the query:     
    """
    query_string = f'site_optional_info(Label, Image, TripID), is_type(Label, "{asset_type}").'

    with PrologMQI() as mqi:
        with mqi.create_thread() as prolog_thread:
            prolog_thread.query("consult(\"project/kb_configuration/KB.pl\")")
            time_list = []
            for i in range(upper_range):
                start = time.time()
                MAIN_QUERY_RESULTS = prolog_thread.query(query_string)
                end = time.time()
                time_list.append(end - start)
    return sum(time_list)/len(time_list)

# execute the query for all the assets in the wikidata_dict on wiki data and on the knowledge base
# this functions simply prints the results for each asset; you can evaluate to change the way it saves the results


for k, v in wikidata_dict.items():
    print(f'{k}:{v} = {wikidata_query_time_evaluation(v, 10)} seconds ON')
    print(f'{k}:{v} = {knowledge_base_time_evaluation(k, 10)} seconds KB')
    print()
