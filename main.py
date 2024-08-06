# Refactored main.py

import os
import sys
import time
from dotenv import load_dotenv
from src.pubsub.webpubsubclient import WebPubSubClient
from src.translation.translationservice import TranslationService
from src.speech.speechprocessor import SpeechProcessor
from src.speech.transcriber import Transcriber

# Load environment variables
load_dotenv()
from src.logutils.logconfig import configure_logging
configure_logging()

import logging
logger = logging.getLogger(__name__)

AZURE_REGION = os.getenv('AZURE_REGION')
TRANSLATOR_KEY = os.getenv('TRANSLATOR_KEY')
PUBSUB_ENDPOINT = os.getenv('PUBSUB_ENDPOINT')
PUBSUB_HUBNAME = os.getenv('PUBSUB_HUBNAME')


# Main Functionality
def main(site_id : str):
    speech_processor = SpeechProcessor(os.getenv('SPEECH_KEY'), AZURE_REGION)
    languages = ['en','bg', 'es','ar','hi', 'zh-Hans','fr']

    translation_service = TranslationService(TRANSLATOR_KEY, AZURE_REGION, languages = languages)
    connection_string = os.getenv("PUBSUB_ENDPOINT")
    publish_service = WebPubSubClient(connection_string, site_id)
    

    transcriber = Transcriber(speech_processor, translation_service, publish_service)
    transcriber.start_transcribing_async()
    transcriber.stop_transcribing_async()

    # Waits for completion.
    while transcriber.is_transcribing():
        time.sleep(.5)

    
if __name__ == "__main__":
    # process the command line arguement to obtain the site_id and if there is none default to 'test_site
    if len(sys.argv) > 1:
        site_id = sys.argv[1]
    else:
        site_id = 'test_site'

    main(site_id)
