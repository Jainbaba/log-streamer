import logging
import json
import re
import time
from datetime import datetime,timezone
import socket

logging.basicConfig(level=logging.INFO)

KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'log_entries'

def listen_socket(producer):
    address = ('fake_log', 9000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Retry loop to connect to the socket server
    while True:
        try:
            logging.info("Attempting to connect to socket...")
            sock.connect(address)
            logging.info("Connected to Socket")
            break
        except socket.error as e:
            logging.error(f"Connection error: {e}, retrying in 5 seconds...")
            time.sleep(5)

    try:
        while True:
            try:
                logging.info("Listening...")
                data = sock.recv(4096)
                if not data:
                    logging.warning("Connection closed by the server.")
                    break
                message = data.decode()
                log_entry = extract_log_details(message)
                if log_entry:
                    try:
                        producer.send(KAFKA_TOPIC, json.dumps(log_entry).encode('utf-8'))
                        producer.flush()
                        logging.info(f"Message Pushed {log_entry}")
                    except Exception as e:
                        logging.error(f"Failed to send message to Kafka: {e}")
            except Exception as e:
                logging.error(f"Error receiving message: {e}")
    finally:
        sock.close()
        logging.info("Socket closed.")

def extract_log_details(log_entry_str: str):
    timestamp_pattern = r"(\d{4}[-/]\d{2}[-/]\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?)"
    level_pattern = r"\[(\w+)\]"  
    request_method_pattern = r"(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)" 
    host_pattern = r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b|(\[[a-fA-F0-9:]+\])|\b[\w.-]+\.[a-zA-Z]{2,}\b"



    
    timestamp_match = re.search(timestamp_pattern, log_entry_str)
    timestamp = timestamp_match.group(1) if timestamp_match else None 
    if timestamp:
        if '/' in timestamp: 
            timestamp = datetime.strptime(timestamp, "%Y/%m/%d %H:%M:%S")
        else:  
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
