import logging
import time
import socket
import random
from faker import Faker
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)


class FakeLogGenerator:
    def __init__(self):
        self.fake = Faker()
        self.sock = None
        self.connected_socket = None

    def setup_socket(self):
        """Setup the socket server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind(("0.0.0.0", 9000))
        self.sock.listen(5)
        logging.info("Socket server started, waiting for connections...")

    def generate_fake_log(self):
        """Generate a fake log entry"""
        log_types = ["INFO", "WARNING", "ERROR"]
        request_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]

        log_entry = (
            f"{datetime.now().isoformat()} "
            f"[{self.fake.random_element(log_types)}] "
            f"{self.fake.random_element(request_methods)} "
            f"{self.fake.ipv4()} "
            f"{self.fake.user_agent()} "
            f"{self.fake.sentence()} "
        )

        return log_entry

    def run(self):
        """Run the fake log generator"""
        self.setup_socket()

        try:
            while True:
                # Accept a new connection if none exists
                if self.connected_socket is None:
                    try:
                        self.connected_socket, address = self.sock.accept()
                        logging.info(f"Connected to {address}")
                    except socket.error as e:
                        logging.error(f"Socket accept error: {e}")
                        time.sleep(1)
                        continue

                # Generate and send a fake log if connected
                log_entry = self.generate_fake_log()
                try:
                    if self.connected_socket:
                        self.connected_socket.sendall(f"{log_entry}\n".encode("utf-8"))
                        logging.info(f"Sent: {log_entry}")
                except (socket.error, BrokenPipeError):
                    logging.warning(
                        "Client disconnected, waiting for new connection..."
                    )
                    self.connected_socket.close()
                    self.connected_socket = None

                # Random sleep before sending the next log
                time.sleep(random.uniform(5, 8))

        except KeyboardInterrupt:
            logging.info("Stopping fake log generator")
        finally:
            if self.connected_socket:
                self.connected_socket.close()
            if self.sock:
                self.sock.close()


if __name__ == "__main__":
    generator = FakeLogGenerator()
    generator.run()
