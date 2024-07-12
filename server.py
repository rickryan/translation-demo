import os
from flask import Flask, redirect, render_template, request, jsonify, send_file
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from dotenv import load_dotenv
from src.genai.summarize import summarize
from src.pubsub.webpubsubclient import WebPubSubClient

load_dotenv()

app = Flask(__name__)

# Initialize Web PubSub service client with connection string and hub name from environment variables
connection_string = os.getenv("PUBSUB_ENDPOINT")
if not connection_string:
    raise ValueError("WEBPUBSUB_CONNECTION_STRING environment variable not set.")

# This function dynamically creates a service client based on the site_id
def get_service_client_for_site(site_id):
    hub_name = f"{site_id}_stream"  # Example of dynamically setting the hub name
    return WebPubSubServiceClient.from_connection_string(connection_string, hub=hub_name)


@app.route('/<site_id>')
def index(site_id=None):
    return render_template('index.html', site_id=site_id)
    #return send_file('public/index.html')

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
    #return jsonify({'summary': translated_summary, 'language' : language})


if __name__ == '__main__':
    app.run()
