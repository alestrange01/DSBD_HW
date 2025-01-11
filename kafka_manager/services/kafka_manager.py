from confluent_kafka.admin import AdminClient
from confluent_kafka import KafkaException
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaConsumer
import logging
from contextlib import closing

logging = logging.getLogger(__name__)


class KafkaManager:

    def __init__(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers

    def get_metadata(self):
        admin_client = AdminClient({'bootstrap.servers': ','.join(self.bootstrap_servers)})
        try:
            logging.info("Fetch dei metadati dal cluster Kafka...")
            metadata = admin_client.list_topics(timeout=10)

            if not metadata.brokers:
                logging.warning("Nessun broker trovato nel cluster.")
                return
            
            logging.info("Brokers nel cluster Kafka:")
            for broker in metadata.brokers.values():
                logging.info(f"Broker ID: {broker.id}, Host: {broker.host}, Porta: {broker.port}")

            if not metadata.topics:
                logging.warning("Nessun topic trovato nel cluster.")
                return

            logging.info("Topic e Partizioni:")
            for topic, topic_metadata in metadata.topics.items():
                logging.info(f"Topic: {topic}")
                if topic_metadata.error:
                    logging.error(f"Errore per il topic '{topic}': {topic_metadata.error}")
                else:
                    for partition_id, partition_metadata in topic_metadata.partitions.items():
                        leader = partition_metadata.leader
                        replicas = partition_metadata.replicas
                        isrs = partition_metadata.isrs
                        logging.info(f"  Partizione {partition_id}:")
                        logging.info(f"    Leader: Broker {leader}")
                        logging.info(f"    Repliche: {replicas}")
                        logging.info(f"    Repliche In-Sync (ISR): {isrs}")

        except KafkaException as e:
            logging.error(f"Errore durante il fetch dei metadati: {e}")
        except Exception as e:
            logging.exception(f"Errore imprevisto durante il fetch dei metadati: {e}")
        finally:
            logging.info("Operazione di fetch dei metadati completata.")


    def list_topics_and_details(self):
        consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers)
        topics = consumer.topics()  
        logging.info("\nDettagli dei Topics disponibili:")

        for topic in sorted(topics):
            partitions = consumer.partitions_for_topic(topic)
            if partitions:
                logging.info(f"\nTopic: {topic}")
                logging.info(f"  Numero partizioni: {len(partitions)}")
                logging.info("  Dettagli delle Partizioni:")
                for partition in sorted(partitions):
                    logging.info(f"    Partizione {partition}")
            else:
                logging.info(f"\nTopic: {topic}")
                logging.info("  Non ci sono partizioni disponibili per questo topic.")

        consumer.close()

    def create_topic_if_not_exists(self,topic_list, num_partitions, replication_factor):
        with closing(KafkaAdminClient(bootstrap_servers=self.bootstrap_servers, client_id='kafka-admin-container')) as admin_client:
            with closing(KafkaConsumer(bootstrap_servers=self.bootstrap_servers)) as consumer:
                for topic in topic_list:
                    if topic not in consumer.topics():
                        new_topic = NewTopic(
                            name=topic,
                            num_partitions=num_partitions,
                            replication_factor=replication_factor
                        )
                        try:
                            logging.info(f"\nCreazione del topic '{topic}'...")
                            admin_client.create_topics(new_topics=[new_topic], validate_only=False)
                            logging.info(f"Topic '{topic}' creato con successo, numero partizioni:{num_partitions} e fattore di replica:{replication_factor}.")
                        except Exception as e:
                            logging.error(f"Si è verificato un errore durante la creazione del topic, codice di errore: {e}")
                    else:
                        logging.info(f"\nIl Topic '{topic}' esiste già.")