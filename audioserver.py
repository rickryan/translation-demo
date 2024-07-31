from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import azure.cognitiveservices.speech as speechsdk
from src.pubsub.webpubsubclient import WebPubSubClient
from src.translation.translationservice import TranslationService
from src.speech.socketspeechprocessor import SpeechProcessor
from src.speech.transcriber import Transcriber
from src.speech.audiostreamconverter import AudioStreamConverter

import os
import io
import queue
import time
import threading

from src.logutils.logconfig import configure_logging
configure_logging()
import logging

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# allow CORS for testing only
socketio = SocketIO(app, cors_allowed_origins='*')
# Assuming the SpeechProcessor class is defined as shown in the excerpt

# Replace 'your_speech_key' and 'your_service_region' with your Azure Speech service subscription key and region
speech_key = os.getenv('SPEECH_KEY')
AZURE_REGION = os.getenv('AZURE_REGION')
TRANSLATOR_KEY = os.getenv('TRANSLATOR_KEY')
PUBSUB_ENDPOINT = os.getenv('PUBSUB_ENDPOINT')
PUBSUB_HUBNAME = os.getenv('PUBSUB_HUBNAME')
target_language = 'fr'  # For French translation, for example
languages = ['en','fr'] # ['en','bg', 'es','ar','hi', 'zh-Hans','fr']
# Create a PushAudioInputStream for streaming audio data
input_queue = None
converted_stream = None
speechprocessor = None
transcriber = None
audio_converter = None
site_id = 'test_site'
temp_inputfile = None
#transcriber.start_transcribing_async()
#transcriber.stop_transcribing_async()

audioChunks = []

@app.route('/')
def index():
    return render_template('audio.html')  

@socketio.on('connect')
def test_connect():
    logger.info('Client connected')

@socketio.on('audio_start')
def start_audio_stream():
    global input_queue, converted_stream, transcriber, speech_processor, audio_converter, temp_inputfile
    logger.info('Starting audio stream')
    input_queue = queue.Queue()
    #input_stream = open('recording.webm', 'rb')
    converted_stream = speechsdk.audio.PushAudioInputStream()
    #converted_stream = open('converted_stream.wav', 'wb')
    audio_converter = AudioStreamConverter(input_queue, converted_stream)
    # create a file to copy the received data into
    temp_inputfile = open('recording_input.webm', 'wb')
    # wiat 2 seconds for the stream to be ready
    time.sleep(2)
    #audio_converter.convert_stream()
    threading.Thread(target=audio_converter.convert_stream).start()
    # Instantiate the SpeechProcessor
    speech_processor = SpeechProcessor(speech_key, AZURE_REGION, converted_stream, target_language)
    speech_processor.start_continuous_recognition()
    #translation_service = TranslationService(TRANSLATOR_KEY, AZURE_REGION, languages = languages)
    #connection_string = os.getenv("PUBSUB_ENDPOINT")
    #publish_service = WebPubSubClient(connection_string, site_id)
    #transcriber = Transcriber(speech_processor, translation_service, publish_service)
    #transcriber.start_transcribing_async()
    #transcriber.stop_transcribing_async()
    #audio_converter.start_conversion()
    emit('audio_started', {'status': 'success'})
    
@socketio.on('audio_done')
def stop_audio_stream():
    global input_queue, audio_converter, converted_stream # transcriber, speech_processor
    logger.info('Stopping audio stream')
    #transcriber.stop_transcribing_async()\
    time.sleep(2)
    converted_stream.close()
    #temp_inputfile.close()
    speech_processor.stop_continuous_recognition()
    audio_converter.cleanup()
    input_queue.put(None)
    logger.debug('Audio stream closed')


@socketio.on('disconnect')
def test_disconnect():
    global input_queue, transcriber
    input_queue.put(None)
    speech_processor.stop_continuous_recognition()
    #transcriber.transcribing_stop()
    logger.info('Client disconnected')

#audio_converter = AudioConverter() 

def float_to_16bit_pcm(outputstream, input_samples, sample_rate=16000, original_sample_rate=48000):
    from struct import pack
    
    logger.debug(f'Converting audio data to 16-bit PCM {len(input_samples)} bytes')
    for i in range(len(input_samples)):
        sample_index = int(i * (original_sample_rate / sample_rate))
        if sample_index < len(input_samples):
            s = max(-1, min(1, input_samples[sample_index]))
            packed_value = pack('<h', int(s * 0x8000) if s < 0 else int(s * 0x7FFF))
            logger.debug(f'Packed value: {len(packed_value)}')
            outputstream.write(packed_value)

            
@socketio.on('audio_data_weba')
def convert_weba(data):
    global converted_stream, input_queue
    logger.debug(f'Received audio data {len(data)}')
    # Convert data to bytes if necessary
    if not isinstance(data, bytes):
        logger.warn('converting to bytes')
        data = data.read()
    # Write the audio to the input stream
    input_queue.put(data)
    temp_inputfile.write(data)

    logger.debug(f'Wrote audio data to stream: {len(data)} bytes')
    emit('transcription', {'length': len(data)})


@socketio.on('audio_data')
def handle_audio_stream(data):
    #global transcriber
    logger.debug(f'Received audio data {len(data)}')
    # Convert data to bytes if necessary
    if not isinstance(data, bytes):
        logger.warn('converting to bytes')
        data = data.read()
    # Write the audio to the input queue
    input_queue.put(data)
    #converted_stream.write(data)
    logger.debug(f'Wrote audio data to stream: {len(data)} bytes')
    #logger.debug(f'Transcriber: {type(transcriber)}')
    if transcriber is not None and transcriber.is_transcribing():
        logger.debug('Transcriber is transcribing')
    # For demonstration, echo back the data length
    emit('transcription', {'length': len(data)})


if __name__ == '__main__':
    logger.info('Starting server')
    socketio.run(app, debug=True)