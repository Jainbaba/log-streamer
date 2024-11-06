import logging
import json
import re
from datetime import datetime,timezone
import socket

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Kafka configuration
KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'log_entries'

def listen_socket(producer):
    address = ("tp.superapi.cloud", 9000)
    try:
        logging.info("Attempting to connect to socket...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(f"address: {address}")
        sock.connect(address)
        logging.info("Connected to Socket")
        while True:
            try:
                logging.info("Listening..")
                data = sock.recv(9000)  # Use socket.recv for synchronous reading
                if not data:
                    logging.warning("Connection closed by the server.")
                    break  # Connection closed
                message = data.decode()  # Decode bytes to string
                log_entry = extract_log_details(message)  # Call the new function
                if log_entry:
                    try:
                        producer.send(KAFKA_TOPIC, json.dumps(log_entry).encode('utf-8'))  # Send JSON message to Kafka
                        producer.flush()  # Ensure the message is sent
                        logging.info(f"Message Pushed {log_entry}")
                    except Exception as e:
                        logging.error(f"Failed to send message to Kafka: {e}")
            except Exception as e:
                logging.error(f"Error receiving message: {e}")
    except Exception as e:
        logging.error(f"Connection error: {e}")
    finally:
        sock.close()  # Close the socket
        logging.info("Socket closed.")

def parse_log_entry(log_entry_str):
    log_pattern = re.compile(
        r"(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[(?P<level>\w+)\] (?P<process_id>\d+#\d+): \*(?P<request_id>\d+) "
        r'(?P<message>.*?failed \(\d+: .*?\))[, ] client: (?P<client_ip>[\d\.]+), server: , request: "(?P<request_method>\w+) '
        r'(?P<request_path>.*?) HTTP/(?P<http_version>\d\.\d)", host: "(?P<host>.*?)"'
    )
    
    try:
        match = log_pattern.match(log_entry_str)
        if match:
            log_entry = {
                'timestamp': datetime.strptime(match.group('timestamp'), "%Y/%m/%d %H:%M:%S").isoformat(),
                'level': match.group('level'),
                'process_id': match.group('process_id'),
                'request_id': int(match.group('request_id')),
                'message': match.group('message'),
                'client_ip': match.group('client_ip'),
                'request_method': match.group('request_method'),
                'request_path': match.group('request_path'),
                'http_version': match.group('http_version'),
                'host': match.group('host'),
                'log_string': log_entry_str,
            }
            return log_entry
    except Exception as e:
        logging.error(f"Error parsing log entry: {e}")
    return None

def extract_log_details(log_entry_str: str):
    timestamp_pattern = r"(\d{4}[-/]\d{2}[-/]\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?)"
    level_pattern = r"\[(\w+)\]"  # Matches [info], [ERROR], etc.
    request_method_pattern = r"\"(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)"  # Extracts HTTP method
    host_pattern = r"(\d+\.\d+\.\d+\.\d+)"  # Extracts the IP address after 'client'

    # Extract timestamp (generic across all formats)
    timestamp_match = re.search(timestamp_pattern, log_entry_str)
    timestamp = timestamp_match.group(1) if timestamp_match else None 
    if timestamp:
        if '/' in timestamp:  # For format like 2024/11/06 07:21:44
            timestamp = datetime.strptime(timestamp, "%Y/%m/%d %H:%M:%S")
        else:  # For format like 06/Nov/2024:07:22:36.125 +0000
            timestamp = datetime.strptime(timestamp, "%d/%b/%Y:%H:%M:%S.%f %z")
    else:
        timestamp = datetime.now()
         
    date_time = timestamp.astimezone(timezone.utc)
    date_time = date_time.isoformat()
    timestamp = timestamp.timestamp()
    
    level_match = re.search(level_pattern, log_entry_str)
    level = level_match.group(1) if level_match else "INFO"

    request_method_match = re.search(request_method_pattern, log_entry_str)
    request_method = request_method_match.group(1).upper() if request_method_match else "unknown"

    host_match = re.search(host_pattern, log_entry_str)
    host = host_match.group(1) if host_match else "unknown"
    
    log_entry = {
        'timestamp': str(timestamp),
        'date_time': date_time,
        'level': level,
        'request_method': request_method,
        'host': host,
        'log_string': log_entry_str,
    }
    return log_entry