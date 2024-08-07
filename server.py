import os
import json
from flask import Flask, redirect, render_template, request, jsonify
from dotenv import load_dotenv
from src.genai.summarize import summarize
from src.pubsub.webpubsubclient import WebPubSubClient
from flask_socketio import emit, SocketIO
from src.speech.audiostreamhandler import AudioStreamHandler
from src.barcode.barcode import generate_qr_code, generate_qr_code_speaker

import logging
from src.logutils.logconfig import configure_logging
configure_logging()

load_dotenv()
SPEECH_KEY = os.getenv('SPEECH_KEY')
AZURE_REGION = os.getenv('AZURE_REGION')
TRANSLATOR_KEY = os.getenv('TRANSLATOR_KEY')
PUBSUB_ENDPOINT = os.getenv('PUBSUB_ENDPOINT')

target_language = 'fr'  # For French translation, for example

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

logger = logging.getLogger(__name__)
site_id = 'test_site'
audio_handler = AudioStreamHandler(SPEECH_KEY, AZURE_REGION, TRANSLATOR_KEY, PUBSUB_ENDPOINT)

# Initialize Web PubSub service client with connection string and hub name from environment variables
connection_string = PUBSUB_ENDPOINT
if not connection_string:
    raise ValueError("WEBPUBSUB_CONNECTION_STRING environment variable not set.")

# Load languages from JSON file
with open('languages.json', 'r') as f:
    languages = json.load(f)['languages']
    # create an array of language codes
    language_codes = [lang['code'] for lang in languages]
    
# returns the list of languages
# for the dropdown in the UI
# returns a JSON object
# Note: currently the same for all sites
# but uses site_id so it can be customized per site    
def get_language_dict_for_site(site_id):
    return languages

# route that returns the list of languages for the specified site
# returns a JSON object of the form:
# [{"code": "en", "name": "English"}, ...]
@app.route('/<site_id>/languages')
def get_languages(site_id=None):
    return jsonify(get_language_dict_for_site(site_id))

# **************************************************************************** #
# routes related to displaying a sites' translations
# **************************************************************************** #

# route that displays the main page for a site
# that will show the translations for the site
@app.route('/<site_id>')
def index(site_id=None):
    return render_template('index.html', site_id=site_id)

# route that negotiaties a token for a site
# returns a JSON object with the token URL
# that the client can use to connect to the Web PubSub service
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

# routes for utility functions to summarize content
# and translate it to a target language
# returns a JSON object with the translated summary
# the summary is generated using the GenAI API
# POST Parameters:
# language: the target language for the translation
#      (e.g. 'fr' for French)
# text: the text to summarize and translate
@app.route('/summarize', methods=['POST'])
def create_summary():
    # Extract 'language' and 'text' from the POST request's body
    if not request.json or not 'language' in request.json or not 'text' in request.json:
        return jsonify({'error': 'Missing data in request'}), 400

    language = request.json['language']
    text_to_summarize = request.json['text']

    translated_summary = summarize(text_to_summarize, language)

    return translated_summary

# route for testing, shows english hidden frame and prepopulates it with the text
@app.route('/test')
def testmode(site_id=None):
    return redirect('/test_site?testmode=true', code=302)


# **************************************************************************** #
# speaker related routes for dealing with audio
# **************************************************************************** #

# route that displays the page for the speaker
# that will allow the speaker to publish audio input
# and translations for a site
# the page creates a socket connection for audio processing
@app.route('/<site_id>/speaker')
def speaker(site_id=None):
    return render_template('speaker.html', site_id=site_id)

@socketio.on('connect')
def test_connect():
    logger.info('Client connected')

# processing for message from socket that starts the audio stream
# Parameters:
# site: the site ID
# source_language: the language of the audio input
@socketio.on('audio_start')
def start_audio_stream(site, source_language):
    try:
        audio_handler.start_audio_stream(site, language_codes, source_language)
        emit('audio_started', {'status': 'success'})
    except Exception as e:
        emit('audio_started', {'status': 'error', 'message': str(e)})
        logger.error(f'Error starting audio stream: {e}')

# processing for message from socket that stops the audio stream
# and associated speak recognition and translation
@socketio.on('audio_done')
def stop_audio_stream():
    try:
        audio_handler.stop_audio_stream()
        emit('audio_stopped', {'status': 'success'})
    except Exception as e:
        emit('audio_stopped', {'status': 'error', 'message': str(e)})
        logger.error(f'Error stopping audio stream: {e}') 

# processing for message from socket that indicate a disconnection 
@socketio.on('disconnect')
def test_disconnect():
    if audio_handler.is_audio_stream_running():
        audio_handler.stop_audio_stream()
    logger.info('Client disconnected')

# processing for audio data from the socket
# Parameters:
# data: the audio data in webm format
# the audio data is written to the audio stream,
# converted to wav format, recognized using the speech API,
# translated to the target languages using the translator API
# the original text and translated text is sent to the Web PubSub service
# and a transcription message is sent back to the client
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


# **************************************************************************** #
# QR code related routes
# **************************************************************************** #

# route to generate a QR code that contains a link to a
# page that will display a single language for a given site
# Parameters:
# site_id: the site ID
# language: the language code for the language to display
# returns a PNG image of the QR code
@app.route('/generate_qr', methods=['GET'])
def generate_qr():
    base_url = request.host_url
    site_id = request.args.get('site_id')
    language = request.args.get('language')
    
    # get the list of supported languages for the site
    languages = get_language_dict_for_site(site_id)
    language_codes = [lang['code'] for lang in languages]
    # check if the language is in the list
    if language not in language_codes:
        return "Language not supported", 400
    
    if not base_url or not site_id or not language:
        return "Missing required parameters", 400
    
    return generate_qr_code(base_url, site_id, language)

# route to display a page that will show QR codes
# with links to a page for each language supported by a site
# and a link to a page the speaker can use for audio input
@app.route('/<site_id>/display_qr_codes', methods=['GET'])
def display_qr_codes(site_id):
    return render_template('display_qr_codes.html', site_id=site_id)

# route to generate a QR code that contains a link to a
# page that the speaker can use to send audio input
@app.route('/<site_id>/generate_qr_speaker', methods=['GET'])
def generate_qr_speaker(site_id):
    base_url = request.host_url
    return generate_qr_code_speaker(base_url, site_id)

if __name__ == '__main__':
    app.run()
