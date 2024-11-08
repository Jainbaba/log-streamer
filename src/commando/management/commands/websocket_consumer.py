import logging
import json
from  datetime import datetime
import asyncio
from kafka import KafkaConsumer  # Use kafka-python
from channels.layers import get_channel_layer
from django.core.management.base import BaseCommand
from home.models import LogEntry,Level,Host,RequestMethod

# Logging configuration
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = "Consume messages from Kafka and send them over WebSocket"

    def create_kafka_consumer(self):
        """Create a synchronous Kafka consumer."""
        consumer = KafkaConsumer(
            "log_entries",  
            bootstrap_servers="kafka:9092",
            group_id="log_entry_consumer_group",  
            enable_auto_commit=True,
            auto_offset_reset="earliest",  
        )
        logging.info("Kafka consumer started")
        return consumer

    def save_log_entry(self, log_entry):
        """Save the log entry to the database with foreign key associations."""
        level_instance = Level.objects.get_or_create(level_type=log_entry["level"].upper())[0]
        request_method_instance = RequestMethod.objects.get_or_create(
            request_method_type=log_entry["request_method"].upper()
        )[0]
        host_instance = Host.objects.get_or_create(host_name=log_entry["host"].upper())[0]
        logging.info(f"Saved log timestamp: {log_entry["timestamp"]}")
    
        log_entry_model = LogEntry(
            timestamp=log_entry["timestamp"],
            date_time=datetime.fromtimestamp(float(log_entry["timestamp"])),
            level=level_instance,
            request_method=request_method_instance,
            host=host_instance,
            log_string=log_entry["log_string"],
        )
        log_entry_model.save()
        logging.info(f"Saved log entry: {log_entry_model}")

    async def send_message_to_websocket(self, log_entry):
        """Asynchronous function to send messages to WebSocket."""
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "log_entries",  
            {"type": "send_log_entry", "message": log_entry},
        )
        logging.info("Message sent to WebSocket")

    def consume_messages(self, consumer):
        """Consume messages from Kafka and send them to WebSocket."""
        try:
            for message in consumer:
                encoded_message = message.value.decode('utf-8', errors='ignore').replace("\x00", "")
                log_entry = json.loads(
                    encoded_message
                )
                if len(log_entry["log_string"]) < 75:
                    logging.info(f"Sending message to WebSocket: {log_entry}")
                    asyncio.run(self.send_message_to_websocket(log_entry))
                    self.save_log_entry(log_entry)
        except Exception as e:
            logging.error(f"Error consuming messages: {e}")
        finally:
            consumer.close()  
            logging.info("Kafka consumer stopped.")

    def handle(self, *args, **kwargs):
        """Run the Kafka consumer."""
        consumer = self.create_kafka_consumer() 
        try:
            self.consume_messages(consumer) 
        finally:
            consumer.close()  
            logging.info("Kafka consumer stopped.")
