from azure.messaging.webpubsubservice import WebPubSubServiceClient
import os
import logging
logger = logging.getLogger(__name__)

class WebPubSubClient:
    def __init__(self, connection_string, site_id):
        self.site_id = site_id
        self.hub_name = f"{site_id}_stream"  # Example of dynamically setting the hub name
        self.service = WebPubSubServiceClient.from_connection_string(connection_string, hub=self.hub_name)
        logger.debug(f"WebPubSubClient initialized for site {site_id}")

    def get_client_access_token(self, roles):
        return self.service.get_client_access_token(roles=roles)

    def send_to_group(self, group_name, message):
        self.service.send_to_group(group_name, message)
        
    def send_to_all(self, message, **kwargs):
        return self.service.send_to_all(message, **kwargs)

    def join_group(self, group_name, user_id):
        self.service.add_user_to_group(group_name, user_id)

    def leave_group(self, group_name, user_id):
        self.service.remove_user_from_group(group_name, user_id)
