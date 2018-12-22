from .migrator import Migrator


def run_migration(migrator: Migrator):
    migrator.migrate()


def run_migrated_tickets_update(migrator: Migrator):
    migrator.update_migrated_tickets()


def start():
    migrator = Migrator()
    while True:
        print("Enter an action to perform:")
        print("    1 - Migrate Zendesk tickets to JIRA")
        print("    2 - Notify migrated tickets' requesters")
        print("    9 - Quit")
        action = int(input("Enter Action: "))
        switcher = {
            1: run_migration,
            2: run_migrated_tickets_update,
            9: quit
        }
        func = switcher.get(action, None)
        if action == 9:
            func()
        elif func is not None :
            func(migrator)
