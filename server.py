import os
from flask import Flask, redirect, render_template, request, jsonify
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from dotenv import load_dotenv
from src.genai.summarize import summarize
from src.pubsub.webpubsubclient import WebPubSubClient
from flask_socketio import emit, SocketIO
from src.speech.audiostreamhandler import AudioStreamHandler

import logging
from src.logutils.logconfig import configure_logging
configure_logging()

load_dotenv()
SPEECH_KEY = os.getenv('SPEECH_KEY')
AZURE_REGION = os.getenv('AZURE_REGION')
TRANSLATOR_KEY = os.getenv('TRANSLATOR_KEY')
PUBSUB_ENDPOINT = os.getenv('PUBSUB_ENDPOINT')

target_language = 'fr'  # For French translation, for example
languages = ['en','bg', 'es','ar','hi', 'zh-Hans','fr']

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

import logging

logger = logging.getLogger(__name__)
site_id = 'test_site'
audio_handler = AudioStreamHandler(SPEECH_KEY, AZURE_REGION, TRANSLATOR_KEY, PUBSUB_ENDPOINT)

# Initialize Web PubSub service client with connection string and hub name from environment variables
connection_string = PUBSUB_ENDPOINT
if not connection_string:
    raise ValueError("WEBPUBSUB_CONNECTION_STRING environment variable not set.")



@app.route('/<site_id>')
def index(site_id=None):
    return render_template('index.html', site_id=site_id)

@app.route('/test')
def testmode(site_id=None):
    return redirect('/test_site?testmode=true', code=302)
    
@app.route('/<site_id>/negotiate')
def negotiate(site_id):
    print(f'Negotiating for site {site_id}')
    service = WebPubSubClient(connection_string, site_id)
    roles = ['webpubsub.sendToGroup.stream', 'webpubsub.joinLeaveGroup.stream']
    token = service.get_client_access_token(roles=roles)

    token_url = token['url']
    # Add remaining query string parameters to the token URL
    token_url += '&' + '&'.join([f"{key}={value[0]}" for key, value in request.args.items()])

    return jsonify({'url': token_url})

@app.route('/summarize', methods=['POST'])
def create_summary():
    # Extract 'language' and 'text' from the POST request's body
    if not request.json or not 'language' in request.json or not 'text' in request.json:
        return jsonify({'error': 'Missing data in request'}), 400

    language = request.json['language']
    text_to_summarize = request.json['text']

    translated_summary = summarize(text_to_summarize, language)

    return translated_summary

@app.route('/<site_id>/speaker')
def speaker(site_id=None):
    return render_template('speaker.html', site_id=site_id)

@socketio.on('connect')
def test_connect():
    logger.info('Client connected')

@socketio.on('audio_start')
def start_audio_stream(site):
    try:
        audio_handler.start_audio_stream(site, languages, target_language)
        emit('audio_started', {'status': 'success'})
    except Exception as e:
        emit('audio_started', {'status': 'error', 'message': str(e)})
        logger.error(f'Error starting audio stream: {e}')
            
@socketio.on('audio_done')
def stop_audio_stream():
    try:
        audio_handler.stop_audio_stream()
        emit('audio_stopped', {'status': 'success'})
    except Exception as e:
        emit('audio_stopped', {'status': 'error', 'message': str(e)})
        logger.error(f'Error stopping audio stream: {e}') 

@socketio.on('disconnect')
def test_disconnect():
    if audio_handler.is_audio_stream_running():
        audio_handler.stop_audio_stream()
    logger.info('Client disconnected')

@socketio.on('audio_data')
def handle_audio_stream(data):
    logger.debug(f'Received audio data {len(data)}')
    # Convert data to bytes if necessary
    if not isinstance(data, bytes):
        logger.warn('converting to bytes')
        data = data.read()
    # Write the audio to the input queue
    audio_handler.write_audio_chunk(data)
    logger.debug(f'Wrote audio data to stream: {len(data)} bytes')
    # For demonstration, echo back the data length
    emit('transcription', {'length': len(data)})


if __name__ == '__main__':
    app.run()
