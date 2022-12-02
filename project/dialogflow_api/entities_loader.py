import sys
import os
import re

subdir = re.sub("eureka.*","eureka",os.getcwd())
os.chdir(subdir)
sys.path.append('../eureka')

from google.cloud import dialogflow_v2 as dialogflow
from project.config_files.config import DIALOGFLOW_PROJECT_ID
from swiplserver import PrologMQI, PrologError

def create_entity(site_category_label, entities_list):
    client = dialogflow.EntityTypesClient()
    duplicate_entity_type = False

    # check if an entity type exists (entity type = church_building, park, city_walls, etc. - USE THE SAME AS KB)
    for page in client.list_entity_types(parent="projects/{}/agent".format(DIALOGFLOW_PROJECT_ID)).pages:
        for entity in page.entity_types:
            if entity.display_name == site_category_label:
                duplicate_entity_type = True

                # update the entity type with update entities (i.e. entities = Duomo di Pisa, Sant'anna, San Zeno for entity type church_building)
                request = dialogflow.BatchUpdateEntitiesRequest(parent=entity.name, entities=entities_list)
                client.batch_update_entities(request=request)
                break

    if(duplicate_entity_type == False):
        # create the entity type and add entities
        entity_type = dialogflow.EntityType()
        entity_type.display_name = site_category_label
        entity_type.entities = entities_list
        entity_type.kind = dialogflow.EntityType.Kind.KIND_MAP

        request = dialogflow.CreateEntityTypeRequest(parent="projects/{}/agent".format(DIALOGFLOW_PROJECT_ID), entity_type=entity_type)
        client.create_entity_type(request=request)


def query_knowledge_base(kb_name, sites_category_labels):
    subdir = re.sub("eureka.*","eureka/project/kb-configuration",os.getcwd())
    os.chdir(subdir)

    # query prolog KB to retrieve pairs item id, item label according to site_labels passed as input
    with PrologMQI() as mqi:
        with mqi.create_thread() as prolog_thread:
            prolog_thread.query("consult(\"{}.pl\")".format(kb_name))

            for site in sites_category_labels:
                result = prolog_thread.query("{}(Id, Label, _,_,_,_,_,_)".format(site))
                # iterate over query result, if any, and create an entity list 
                entities = []
                for r in result:
                    entity = dialogflow.EntityType.Entity()
                    entity.value = r["Id"]
                    entity.synonyms = [r["Id"], r["Label"]]
                    entities.append(entity)

                if len(entities) > 0:
                    create_entity(site, entities)
                else:
                    print("There are no entities to add.")


def main():
    # add into this list the labels of cultural sites (e.g church_building) used to built the knowledge base, to create the respective entity in Dialogflow
    # PAY ATTENTION: check entities list on Dialogflow before adding something new. No duplicates allowed!!!
    site_category_labels = ["park", "public_garden", "city_walls", "church_building" ] 
    query_knowledge_base("KB", site_category_labels)

main()