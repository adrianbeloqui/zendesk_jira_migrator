from zenpy import Zenpy
from ..settings import ZENDESK_CONNECTION_SETTINGS


class ZendeskClient:

    def __init__(self):
        self.client = self._authenticate()

    def _authenticate(self):
        instance = Zenpy(
            **ZENDESK_CONNECTION_SETTINGS
        )
        return instance