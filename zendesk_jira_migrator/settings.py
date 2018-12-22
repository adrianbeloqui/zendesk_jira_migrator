import os, sys


# Project Settings

DOWNLOAD_PATH = os.path.join(
    os.path.dirname(sys.modules['__main__'].__file__),
    "zendesk_jira_migrator",
    "tmp"
)

DATA_PATH = os.path.join(
    os.path.dirname(sys.modules['__main__'].__file__),
    "zendesk_jira_migrator",
    "data"
)

# JIRA Settings

JIRA_CONNECTION_SETTINGS = {
    "USER": os.getenv("JIRA_USER"),
    "PASSWORD": os.getenv("JIRA_PASSWORD"),
    "OPTIONS": {
        "server": os.getenv("JIRA_URL"),
        "verify": False
    }
}

JIRA_ISSUES_CONFIG = {
    'PROJECT_KEY': os.getenv("JIRA_PROJECT_KEY"),
    'ISSUE_TYPE': 'Story'
}

# Zendesk Settings

ZENDESK_CONNECTION_SETTINGS = {
    "subdomain": os.getenv("ZENDESK_SUBDOMAIN"),
    "email": os.getenv("ZENDESK_USER"),
    "password": os.getenv("ZENDESK_PASSWORD")
}


ZENDESK_VIEWS = []
