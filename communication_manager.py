import socket
import threading
import binascii

import serial


class CommunicationManager:
    def __init__(self, server_ip, server_port, serial_port, baud_rate, log_function=None, log_communication=False,
                 log_hex=False, stop_function=None):

        self.server_ip = server_ip
        self.server_port = server_port
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.log_communication = log_communication
        self.log_hex = log_hex
        self.log_function = log_function

        self.tcp_client = None
        self.serial_conn = None
        self.tcp_to_serial_thread = None
        self.serial_to_tcp_thread = None
        self.running = False
        self.stop_function = stop_function

    def set_print_log(self, is_log):
        self.log_communication = is_log
        print(f"log_communication: {self.log_communication}")

    def set_hex_log(self, is_hex):
        self.log_hex = is_hex
        print(f"log_hex: {self.log_hex}")

    def log(self, message):
        if self.log_function:
            self.log_function(message)

    def log_comm(self, data, tag):
        if self.log_communication:
            if self.log_hex:
                self.log(f"{tag}: {binascii.hexlify(data).decode('ascii')}")
            else:
                self.log(f"{tag}:{data}")

    def start(self):
        self.stop()
        self.running = True
        try:
            self.serial_conn = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            print(f"open the serial_conn")
        except serial.SerialException as e:
            self.log(f"Failed to open serial port: {e}")
            return

        # connect tcp
        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.tcp_client.connect((self.server_ip, self.server_port))
        except socket.error as e:
            self.log(f"Could not connect to TCP server: {e}")
            self.serial_conn.close()
            return


        self.tcp_to_serial_thread = threading.Thread(target=self.tcp_to_serial)
        self.serial_to_tcp_thread = threading.Thread(target=self.serial_to_tcp)
        self.tcp_to_serial_thread.start()
        self.serial_to_tcp_thread.start()

    def stop(self):
        self.running = False
        self.stop_tcp_client()
        self.stop_serial_port()
        # if self.tcp_to_serial_thread is not None and self.tcp_to_serial_thread.is_alive():
        #     self.tcp_to_serial_thread.join()
        # if self.serial_to_tcp_thread is not None and self.serial_to_tcp_thread.is_alive():
        #     self.serial_to_tcp_thread.join()

    def stop_tcp_client(self):
        self.running = False
        self.stop_serial_port()
        if self.stop_function:
            self.stop_function()

    def stop_serial_port(self):
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None

    def tcp_to_serial(self):
        """Receive data from TCP and forward it to serial port."""
        while self.running:
            try:
                data = self.tcp_client.recv(1024)
                if data:
                    self.serial_conn.write(data)
                    self.log_comm(data, ">>>")
                if not self.running:
                    break
            except socket.timeout:
                continue
            except socket.error as e:
                self.log(f"TCP to Serial error: {e}")
                break
        self.log("stop tcp_to_serial")
        self.stop_tcp_client()

    def serial_to_tcp(self):
        """Receive data from serial port and forward it to TCP"""
        while self.running:
            try:
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    self.tcp_client.sendall(data)
                    self.log_comm(data, "<<<")
                if not self.running:
                    break
            except serial.SerialException as e:
                self.log(f"Serial to TCP error: {e}")
                break
        self.log("stop serial_to_tcp")
        self.stop_serial_port()
