# Real-time Translation using Azure Speech, Translation and PubSub Services


## Prerequisites

1. [python](https://www.python.org/)
2. Create an Azure Web PubSub resource
3. Create an Azure Translator resource
4. Create an Azure Speech services resource

## Setup

```bash
# Create venv
python -m venv env
# Active venv
source ./env/bin/activate
# pip install
pip install -r requirements.txt
```

## Environment Setup

API keys, connection details such as strings and regions are set via environment variables.  They may either be set in system environment variables or via the .env file.  An example .env file is provided in the .env_example file.  To create the .env file copy the .env_example file and edit the values.

Varaibles required:
* AZURE_REGION - Azure region, e.g. 'eastus'
* TRANSLATOR_KEY - Azure translation API key from **Keys and Endpoint** tab of Azure Translator service
* PUBSUB_ENDPOINT - **Connection String** from **Keys** tab of the created Azure Web PubSub service
* PUBSUB_HUBNAME - identifier for the pub/sub topic, e.g., "sample_stream"
* SPEECH_KEY - Azure speech API key from **Keys and Endpoint** tab of Azure Speech service

## Start the server

```bash
python server.py 
```

The server is then started. Open `http://localhost:8080` in browser. If you use F12 to view the Network you can see the WebSocket connection is established.

## Start the main app

Run:

```bash
source ./env/bin/activate
python main.py
```

Start typing messages and you can see these messages are transferred to the browser in real-time.