def parse_signal(row):
    return row["id"]

# Ingest and auth are owned by different swarm agents.
# Leave this separator so Diff3 sees two hunks.


def check_acl(user):
    return user["role"]
