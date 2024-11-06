import logging
import time
from django.core.management.base import BaseCommand
from home.listeners import listen_socket
from kafka import KafkaProducer  # Use kafka-python

class Command(BaseCommand):
    help = 'Listen to the Socket and sends it to Kafka Message Queue'
    
    def create_kafka_producer(self):
        """Create a synchronous Kafka producer."""
        producer = KafkaProducer(bootstrap_servers='kafka:9092')
        logging.info("Kafka producer started")
        return producer

    def handle(self, *args, **kwargs):
        """Run the socket listener."""
        producer = self.create_kafka_producer() 
        try:
            listen_socket(producer)  # Run the socket listener
        finally:
            producer.close()  # Ensure producer is stopped
            logging.info("Kafka producer stopped.")
