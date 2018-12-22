# Zendesk-Jira Migrator

This project intends to provide a simple way of migrating Zendesk tickets to JIRA without loosing any comments or attachments in the process. Zendesk tickets are meant to be retrieved from a Zendesk view.

When migrating, a binary file for each project key will be stored to keep a list of the migrated tickets with the JIRA issues IDs created. This gives the possibility to update Zendesk tickets anytime after the migration process has been ran. Initially, the intention is to be able to communicate the Zendesk tickets' requesters about the migration performed.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine
for development and testing purposes. See deployment for notes on how to deploy the project
on a live system.

### Prerequisites

This project was built using Python 3.5.1

Install dependencies from requirements.txt

```
pip install -r requirements.txt
```

### Configuration

To run this project a set of environment variables are needed. Also, make sure the rest configuration file meets your expectactions.

| Environment Variable  | Description               |
| --------------------- | ------------------------- |
| JIRA_USER             | JIRA username             |
| JIRA_PASSWORD         | JIRA user's password      |
| JIRA_URL              | JIRA server URL           |
| JIRA_PROJECT_KEY      | JIRA project key          |
| ZENDESK_SUBDOMAIN     | Zendesk subdomain         |
| ZENDESK_USER          | Zendesk username          |
| ZENDESK_PASSWORD      | JIRA user's password      |


### Running

To run this project you simply execute

```
python run.py
```


## Authors

* **Adrian Beloqui** - *Initial work*
