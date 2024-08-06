
import queue
import os
import threading
import azure.cognitiveservices.speech as speechsdk

from src.speech.audiostreamconverter import AudioStreamConverter
from src.speech.socketspeechprocessor import SpeechProcessor
from src.speech.transcriber import Transcriber
from src.translation.translationservice import TranslationService
from src.pubsub.webpubsubclient import WebPubSubClient

import logging
logger = logging.getLogger(__name__)


class AudioStreamHandler:
    def __init__(self, speech_key, azure_region, translator_key, pubsub_endpoint):
        self.speech_key = speech_key
        self.azure_region = azure_region
        self.translator_key = translator_key
        self.pubsub_endpoint = pubsub_endpoint
        self.input_queue = None
        self.converted_stream = None
        self.transcriber = None
        self.speech_processor = None
        self.audio_converter = None

    def start_audio_stream(self, site, languages, target_language):
        logger.info('Starting audio stream')
        self.input_queue = queue.Queue()
        self.converted_stream = speechsdk.audio.PushAudioInputStream()
        self.audio_converter = AudioStreamConverter(self.input_queue, self.converted_stream)
        threading.Thread(target=self.audio_converter.convert_stream).start()
        # Instantiate the SpeechProcessor and set up the transcriber and translation service
        self.speech_processor = SpeechProcessor(self.speech_key, self.azure_region, self.converted_stream, target_language)
        translation_service = TranslationService(self.translator_key, self.azure_region, languages=languages)
        connection_string = self.pubsub_endpoint
        publish_service = WebPubSubClient(connection_string, site)
        self.transcriber = Transcriber(self.speech_processor, translation_service, publish_service)
        self.transcriber.start_transcribing_async()
        logger.debug('Audio stream opened')
        return ({'status': 'success'})

    def stop_audio_stream(self):
        logger.info('Stopping audio stream')
        self.converted_stream.close()
        self.audio_converter.cleanup()
        if self.input_queue is not None:
            self.input_queue.put(None)
        self.transcriber.stop_transcribing_async()
        logger.debug('Audio stream closed')
        
    def write_audio_chunk(self, chunk):
        if self.input_queue is not None:
            self.input_queue.put(chunk)
        
    def is_audio_stream_running(self):
        return self.transcriber is not None and self.transcriber.is_transcribing()