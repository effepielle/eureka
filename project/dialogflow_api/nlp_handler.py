import sys
sys.path.append('../eureka')
from google.cloud import dialogflow_v2 as dialogflow
from project.config_files.config import DIALOGFLOW_PROJECT_ID, DIALOGFLOW_LANGUAGE_CODE

def analyze_input(session_id, message_text):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, session_id)

    text_input = dialogflow.types.TextInput(text=message_text, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(session=session, query_input=query_input)

    return response.query_result.fulfillment_text