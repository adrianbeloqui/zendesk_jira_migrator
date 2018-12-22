import os
import pickle
import time
from zenpy.lib.api_objects import Comment, Ticket
from jira import Issue

from .clients.jira import JiraClient
from .clients.zendesk import ZendeskClient
from .settings import ZENDESK_VIEWS, DOWNLOAD_PATH, DATA_PATH, JIRA_ISSUES_CONFIG


class Migrator:
    """
    Migrator that will take all of the Zendesk tickets from the
    list of Zendesk views provided, and perform a migration to JIRA.

    Each ticket will be migrated as a unique JIRA issue with the basic
    characteristics. Each reply to the Zendesk ticket will be added as a
    comment on the JIRA issue. Each individual attachment on the Zendesk
    ticket will be added the JIRA issue (missing the relationship between
    reply and attachment).

    Each Zendesk ticket will be updated with a private note that shows the
    new JIRA issue key/id related to that ticket.

    A binary file containing a list of (Zendesk ticket ID, JIRA issue ID) tuples
    will be stored in the project's data folder. The application will read this
    file when running the update_migrated_tickets feature to notify the requesters
    of the migrated Zendesk tickets.
    """

    def __init__(self):
        self._zd_authenticate()
        self._jira_authenticate()
        self.migrated_tickets = []
        self.JIRA_PROJECT_KEY = JIRA_ISSUES_CONFIG.get("PROJECT_KEY")
        self.JIRA_ISSUE_TYPE = JIRA_ISSUES_CONFIG.get("ISSUE_TYPE")
        self.ZENDESK_VIEWS = ZENDESK_VIEWS
        self.DOWNLOAD_PATH = DOWNLOAD_PATH
        self.DATA_PATH = DATA_PATH

    def migrate(self):
        tickets = self._zd_get_tickets()
        self._preprocess_tickets(tickets)
        self._migrate_to_jira(tickets)
        self._update_migrated_zd_tickets(tickets)
        self._pickle_migrated_tickets()

    def update_migrated_tickets(self):
        tickets = self._load_tickets()
        tickets = self._from_id_to_tickets(tickets)
        self._update_migrated_tickets_requesters(tickets)

    def _zd_authenticate(self):
        self.zd_client = ZendeskClient().client

    def _jira_authenticate(self):
        self.jira_client = JiraClient().client

    def _zd_get_tickets(self) -> list:
        tickets = []
        for view_id in self.ZENDESK_VIEWS:
            view = self.zd_client.views(id=view_id)
            tickets.extend(view.api.tickets(view))
        return tickets

    def _preprocess_tickets(self, tickets: list):
        for ticket in tickets:
            ticket_reference = "Zendesk Ticket: {0}".format(ticket.id)
            description = "{0} \n\n {1}".format(
                ticket_reference, ticket.description.replace('`', "").replace("#", "")
            )

            issue_dict = {
                'project': {'key': self.JIRA_PROJECT_KEY },
                'summary': ticket.raw_subject.replace("\n", " "),
                'description': description,
                'issuetype': {'name': self.JIRA_ISSUE_TYPE },
            }
            ticket.jira_issue = issue_dict
            ticket.jira_comments = []
            ticket.jira_attachments = []
            self._get_ticket_comments_attachments(ticket)

    def _get_ticket_comments_attachments(self, ticket: Ticket):
        for comment in self.zd_client.tickets.comments(ticket.id):
            ticket.jira_comments.append(comment.plain_body)
            for attachment in comment.attachments:
                ticket_folder = os.path.join(
                    self.DOWNLOAD_PATH,
                    str(ticket.id)
                )
                if not os.path.isdir(ticket_folder):
                    os.mkdir(ticket_folder)

                destination_path = os.path.join(
                    ticket_folder,
                    attachment.file_name
                )
                self.zd_client.attachments.download(
                    attachment_id=attachment.id,
                    destination=destination_path
                )
                ticket.jira_attachments.append(destination_path)

    def _migrate_to_jira(self, tickets: list):
        for ticket in tickets:
            new_issue = self.jira_client.create_issue(fields=ticket.jira_issue)
            ticket.issue_id = new_issue.key
            self.migrated_tickets.append((ticket.id, ticket.issue_id))

            if ticket.jira_comments:
                self._add_jira_issue_comments(new_issue, ticket.jira_comments)
            if ticket.jira_attachments:
                self._add_jira_issue_attachments(new_issue, ticket.jira_attachments)
                ticket_folder = os.path.join(
                    self.DOWNLOAD_PATH,
                    str(ticket.id)
                )
                os.rmdir(ticket_folder)

    def _add_jira_issue_comments(self, issue: Issue, comments: list):
        for comment in comments:
            self.jira_client.add_comment(issue, comment)

    def _add_jira_issue_attachments(self, issue: Issue, attachments: list):
        for attachment in attachments:
            # Some attachments seem to not be found. E.g. ~W0001D
            try:
                self.jira_client.add_attachment(issue=issue, attachment=attachment)
                os.remove(attachment)
            except FileNotFoundError:
                print(
                    "Issue {0}. Failed to upload attachment: {1}".format(
                        issue.key,
                        attachment
                    )
                )

    def _update_migrated_zd_tickets(self, tickets: list):
        self._add_zd_comment(
            tickets,
            lambda x: "This tickets has been migrated to JIRA, "
                      "issue {0}".format(x.issue_id)
        )

    def _add_zd_comment(self, tickets: list, message: callable, public=False):
        """
        Add a private note with the JIRA issue key to each ticket
        """

        for ticket in tickets:
            ticket.comment = Comment(
                body=message(ticket),
                public=public
            )

        if tickets:
            jobs = []
            # Bulk API accepts only 100 items at a time
            while len(tickets) > 100:
                batch = tickets[:100]
                tickets = tickets[100:]
                jobs.append(self.zd_client.tickets.update(batch))
            jobs.append(self.zd_client.tickets.update(tickets))
            self._track_jobs_status(jobs)

    def _track_jobs_status(self, jobs):
        while jobs:
            running_jobs = []
            for job in jobs:
                if job.status not in ["failed", "completed", "killed"]:
                    time.sleep(1)
                    job = self.zd_client.job_status(id=job.id)
                    running_jobs.append(job)
                else:
                    print("Job {0}. URL {1}".format(job.status, job.url))
                    for result in job.results:
                        print("Success:".rjust(12), result.success)
            jobs = running_jobs

    def _pickle_migrated_tickets(self):
        file_name = "{0}_migrated_tickets.bin".format(self.JIRA_PROJECT_KEY)
        for ticket in self.migrated_tickets:
            with open(os.path.join(self.DATA_PATH, file_name), "wb") as f:
                pickle.dump(ticket, f)

    def _load_tickets(self) -> list:
        tickets = []
        file_name = "{0}_migrated_tickets.bin".format(self.JIRA_PROJECT_KEY)
        with open(os.path.join(self.DATA_PATH, file_name), "rb") as f:
            while True:
                try:
                    tickets.append(pickle.load(f))
                except EOFError:
                    break
        return tickets

    def _from_id_to_tickets(self, migrated_tickets: list) -> list:
        tickets = []
        for ticket_id, issue_id in migrated_tickets:
            ticket = self.zd_client.tickets(id=ticket_id)
            ticket.issue_id = issue_id
            tickets.append(ticket)
        return tickets

    def _update_migrated_tickets_requesters(self, tickets: list):
        self._add_zd_comment(
            tickets,
            lambda x: "Dear Requester, \n\n "
                      "This is an update to let you know that we "
                      "have migrated to JIRA. Your card number is {0}. \n\n "
                      "Thank you, \n"
                      "MIB Team".format(x.issue_id),
            public=True
        )
