import subprocess

TOPICS = [
    {"name": "to-alert-system", "partitions": 1, "replication": 1}, #TODO Capire se partitions va bene cosi o se bisogna fare modifiche al consumer
    {"name": "to-notifier", "partitions": 2, "replication": 1}, #TODO Capire se partitions va bene cosi o se bisogna fare modifiche al consumer
]

for topic in TOPICS:
    name = topic["name"]
    partitions = topic["partitions"]
    replication = topic["replication"]

    try:
        result = subprocess.run(
            ["kafka-topics", "--bootstrap-server", "localhost:9092", "--list"],
            capture_output=True, text=True, check=True
        )
        if name not in result.stdout:
            subprocess.run(
                [
                    "kafka-topics", "--bootstrap-server", "localhost:9092", "--create",
                    "--topic", name, "--partitions", str(partitions), "--replication-factor", str(replication)
                ],
                check=True
            )
            print(f"Topic {name} creato con successo.")
        else:
            print(f"Topic {name} esiste già.")
    except subprocess.CalledProcessError as e:
        print(f"Errore durante la gestione del topic {name}: {e}")

while True:
    pass
