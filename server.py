import os
from flask import Flask, request, jsonify, send_file
from azure.messaging.webpubsubservice import WebPubSubServiceClient

app = Flask(__name__)

# Initialize Web PubSub service client with connection string and hub name from environment variables
connection_string = os.getenv("WEBPUBSUB_CONNECTION_STRING")
hub_name = os.getenv("WEBPUBSUB_HUB_NAME", "sample_stream")  # Default hub name is 'sample_stream'

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

if __name__ == '__main__':
    app.run()
