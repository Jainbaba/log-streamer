import logging
import time
import json
import socket
import random
from django.core.management.base import BaseCommand
from faker import Faker
from datetime import datetime


class Command(BaseCommand):
    help = "Generate fake log data and send it to a socket"

    def __init__(self):
        super().__init__()
        self.fake = Faker()
        self.sock = None
        self.connectedSocket = None

    def setup_socket(self):
        """Setup the socket server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('13.127.229.179', 8080))
        self.sock.listen(5)
        self.connectedSocket, address = self.sock.accept()
        logging.info("Socket connection established")

    def generate_fake_log(self):
        """Generate a fake log entry"""
        log_types = ["INFO", "WARNING", "ERROR"]
        request_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]

        log_entry = (
            f"{datetime.now().isoformat()} "
            f"{self.fake.random_element(log_types)} "
            f"{self.fake.uuid4()} "
            f"{self.fake.ipv4()} "
            f"{self.fake.user_agent()} "
            f"{self.fake.random_element(request_methods)} "
            f"{self.fake.sentence()} "
            f"{self.fake.random_element([200, 201, 400, 401, 403, 404, 500])}"
        )

        return log_entry

    def handle(self, *args, **kwargs):
        """Run the fake log generator"""
        try:
            self.setup_socket()

            while True:
                try:
                    log_entry = self.generate_fake_log()
                    self.connectedSocket.send(f"{log_entry}\n".encode("utf-8"))
                    self.stdout.write(f"Sent: {log_entry}")
                    sleep_time = random.uniform(0.3, 1.0)
                    time.sleep(sleep_time)
                except socket.error as e:
                    self.stderr.write(f"Socket error: {e}")
                    break

        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Stopping fake log generator"))
        except socket.error as e:
            self.stderr.write(f"Failed to setup socket: {e}")
        finally:
            if self.connectedSocket:
                self.connectedSocket.close()
            if self.sock:
                self.sock.close()
