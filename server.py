import os
from flask import Flask, request, jsonify, send_file
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from dotenv import load_dotenv
from summarize import summarize

load_dotenv()

app = Flask(__name__)

# Initialize Web PubSub service client with connection string and hub name from environment variables
connection_string = os.getenv("PUBSUB_ENDPOINT")
hub_name = os.getenv("PUBSUB_HUBNAME", "sample_stream")  # Default hub name is 'sample_stream'

if not connection_string:
    raise ValueError("WEBPUBSUB_CONNECTION_STRING environment variable not set.")

service = WebPubSubServiceClient.from_connection_string(connection_string, hub=hub_name)

@app.route('/')
def index():
    return send_file('public/index.html')
    
@app.route('/negotiate')
def negotiate():
    global service
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
