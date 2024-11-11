import logging
import time
import json
import socket
import random
from django.core.management.base import BaseCommand
from faker import Faker
from datetime import datetime

class Command(BaseCommand):
    help = 'Generate fake log data and send it to a socket'

    def __init__(self):
        super().__init__()
        self.fake = Faker()
        self.sock = None

    def setup_socket(self):
        """Setup the socket server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost', 9999)) 
        logging.info("Socket connection established")

    def generate_fake_log(self):
        """Generate a fake log entry"""
        log_types = ['INFO', 'WARNING', 'ERROR']
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': self.fake.random_element(log_types),
            'user_id': self.fake.uuid4(),
            'ip_address': self.fake.ipv4(),
            'user_agent': self.fake.user_agent(),
            'action': self.fake.random_element(['login', 'logout', 'purchase', 'view', 'update']),
            'message': self.fake.sentence(),
            'status_code': self.fake.random_element([200, 201, 400, 401, 403, 404, 500]),
        }
        
        return json.dumps(log_entry)

    def handle(self, *args, **kwargs):
        """Run the fake log generator"""
        self.setup_socket()
        
        try:
            while True:
                log_entry = self.generate_fake_log()
                self.sock.send(f"{log_entry}\n".encode('utf-8'))
                self.stdout.write(f"Sent: {log_entry}")
                sleep_time = random.uniform(0.3, 1.0)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Stopping fake log generator'))
        finally:
            if self.sock:
                self.sock.close()