#!/usr/bin/env python3
import socket
import threading
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from logging.handlers import RotatingFileHandler
import os
import random
from datetime import datetime

# Configuration
CONFIG = {
    "smtp_server": "smtp.your-email-provider.com",
    "smtp_port": 587,
    "smtp_username": "your-email@example.com",
    "smtp_password": "your-email-password",
    "email_recipient": "recipient@example.com",
    "email_subject": "Honeypot Activity Report",
    "listen_ports": [22, 80, 443, 3389, 5900],  # SSH, HTTP, HTTPS, RDP, VNC
    "log_file": "honeypot.log",
    "max_log_size": 1048576,  # 1MB
    "backup_count": 5,
    "fake_responses": {
        22: "SSH-2.0-OpenSSH_7.9p1 Debian-10+deb10u2\r\n",
        80: "HTTP/1.1 200 OK\r\nServer: nginx/1.18.0\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Welcome to our server</h1></body></html>\r\n",
        443: "HTTP/1.1 200 OK\r\nServer: nginx/1.18.0\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Secure site</h1></body></html>\r\n",
        3389: "\x03\x00\x00\x13\x0e\xd0\x00\x00\x124\x00\x02\x00\x08\x00\x02\x00\x00\x00",  # RDP connection response
        5900: "RFB 003.008\n"  # VNC response
    }
}

class Honeypot:
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger("honeypot")
        self.active_connections = 0
        self.total_connections = 0
        self.connections = {}
        
    def setup_logging(self):
        """Configure logging to file with rotation"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                RotatingFileHandler(
                    CONFIG['log_file'],
                    maxBytes=CONFIG['max_log_size'],
                    backupCount=CONFIG['backup_count']
                )
            ]
        )
    
    def handle_connection(self, client_socket, port, client_address):
        """Handle incoming connection"""
        self.active_connections += 1
        self.total_connections += 1
        connection_id = f"{client_address[0]}:{client_address[1]}-{time.time()}"
        self.connections[connection_id] = {
            "ip": client_address[0],
            "port": client_address[1],
            "timestamp": datetime.now().isoformat(),
            "honeypot_port": port,
            "data_exchanged": []
        }
        
        try:
            # Log the connection
            self.logger.info(f"New connection from {client_address} to port {port}")
            
            # Send fake response if configured
            if port in CONFIG['fake_responses']:
                client_socket.sendall(CONFIG['fake_responses'][port].encode())
            
            # Simulate service interaction
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    # Log received data
                    self.connections[connection_id]['data_exchanged'].append({
                        "timestamp": datetime.now().isoformat(),
                        "direction": "inbound",
                        "data": data.hex()  # Store as hex to avoid encoding issues
                    })
                    
                    self.logger.info(f"Data received from {client_address}: {data.hex()}")
                    
                    # Send random response to keep connection alive
                    if random.random() > 0.7:
                        response = b"ACK " + str(random.randint(1000, 9999)).encode() + b"\r\n"
                        client_socket.sendall(response)
                        self.connections[connection_id]['data_exchanged'].append({
                            "timestamp": datetime.now().isoformat(),
                            "direction": "outbound",
                            "data": response.hex()
                        })
                        
                except (socket.timeout, ConnectionResetError):
                    break
                    
        except Exception as e:
            self.logger.error(f"Error handling connection from {client_address}: {str(e)}")
        finally:
            client_socket.close()
            self.active_connections -= 1
            self.logger.info(f"Connection from {client_address} closed")
    
    def start_server(self, port):
        """Start a honeypot server on specified port"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', port))
            server_socket.listen(5)
            self.logger.info(f"Honeypot started on port {port}")
            
            while True:
                client_socket, client_address = server_socket.accept()
                client_socket.settimeout(30)  # 30 second timeout
                threading.Thread(
                    target=self.handle_connection,
                    args=(client_socket, port, client_address),
                    daemon=True
                ).start()
                
        except Exception as e:
            self.logger.error(f"Error starting server on port {port}: {str(e)}")
    
    def send_email_report(self):
        """Send email report with honeypot activity"""
        try:
            # Prepare email content
            message = MIMEMultipart()
            message['From'] = CONFIG['smtp_username']
            message['To'] = CONFIG['email_recipient']
            message['Subject'] = CONFIG['email_subject']
            
            # Read log file
            with open(CONFIG['log_file'], 'r') as f:
                log_content = f.read()
            
            # Create email body
            body = f"""
            Honeypot Activity Report - {datetime.now().isoformat()}
            =============================================
            
            Summary:
            - Total connections: {self.total_connections}
            - Active connections: {self.active_connections}
            
            Recent Connections:
            {json.dumps(self.connections, indent=2)}
            
            Log File Contents:
            {log_content}
            """
            
            message.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(CONFIG['smtp_server'], CONFIG['smtp_port']) as server:
                server.starttls()
                server.login(CONFIG['smtp_username'], CONFIG['smtp_password'])
                server.send_message(message)
            
            self.logger.info("Email report sent successfully")
            
        except Exception as e:
            self.logger.error(f"Error sending email report: {str(e)}")
    
    def start(self):
        """Start all honeypot servers and reporting"""
        # Start honeypot servers in separate threads
        for port in CONFIG['listen_ports']:
            threading.Thread(
                target=self.start_server,
                args=(port,),
                daemon=True
            ).start()
        
        # Start periodic email reporting
        def reporting_loop():
            while True:
                time.sleep(3600)  # Send report every hour
                self.send_email_report()
        
        threading.Thread(target=reporting_loop, daemon=True).start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)

if __name__ == "__main__":
    honeypot = Honeypot()
    honeypot.start()
