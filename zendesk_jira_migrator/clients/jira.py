from jira import JIRA
from ..settings import JIRA_CONNECTION_SETTINGS


class JiraClient:

    def __init__(self):
        self.client = self._authenticate()

    def _authenticate(self):
        jira_instance = JIRA(
            JIRA_CONNECTION_SETTINGS.get("OPTIONS"),
            basic_auth=(
                JIRA_CONNECTION_SETTINGS.get("USER"),
                JIRA_CONNECTION_SETTINGS.get("PASSWORD")
            )
        )
        return jira_instance
