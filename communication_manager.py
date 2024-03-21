import socket
import threading
import binascii
import time

import serial


class CommunicationManager:
    def __init__(self, server_ip, server_port, serial_port, baud_rate, log_function=None, log_communication=False,
                 log_hex=False, stop_function=None, enable_heartbeat=False, heartbeat_data='', heartbeat_interval=0,
                 heart_hex=False, auto_reconnect=True):

        self.server_ip = server_ip
        self.server_port = server_port
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.log_communication = log_communication
        self.log_hex = log_hex
        self.log_function = log_function
        self.auto_reconnect = auto_reconnect

        # Heartbeat settings
        self.enable_heartbeat = enable_heartbeat
        self.heartbeat_data = heartbeat_data
        self.heartbeat_interval = heartbeat_interval
        self.heart_hex = heart_hex

        self.tcp_client = None
        self.serial_conn = None
        self.tcp_to_serial_thread = None
        self.serial_to_tcp_thread = None
        self.running = False
        self.stop_function = stop_function
        self.heartbeat_thread = None
        self.heartbeat_event = threading.Event()  # 创建一个事件对象

    def set_auto_reconnect(self, auto_reconnect):
        self.auto_reconnect = auto_reconnect

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
        self.try_connect_serial_port()
        self.try_connect_tcp_server()

        self.tcp_to_serial_thread = threading.Thread(target=self.tcp_to_serial)
        self.serial_to_tcp_thread = threading.Thread(target=self.serial_to_tcp)
        self.tcp_to_serial_thread.start()
        self.serial_to_tcp_thread.start()

        if self.enable_heartbeat:
            self.heartbeat_thread = threading.Thread(target=self.send_heartbeat)
            self.heartbeat_thread.start()

    def try_connect_serial_port(self):
        # 尝试建立串口连接
        try:
            self.serial_conn = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            print("Opened the serial connection.")
        except serial.SerialException as e:
            self.log(f"Failed to open serial port: {e}")
            if self.auto_reconnect:
                self.log(f"Attempting to reconnect serial port: {e} in 3 seconds...")
                time.sleep(3)
                self.try_connect_serial_port()
            return

    def try_connect_tcp_server(self):
        # 尝试连接TCP服务器
        try:
            self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_client.connect((self.server_ip, self.server_port))
        except socket.error as e:
            self.log(f"Could not connect to TCP server: {e}")
            if self.auto_reconnect:
                self.log("Attempting to reconnect in 3 seconds...")
                time.sleep(3)
                self.try_connect_tcp_server()

    def tcp_to_serial(self):
        """Receive data from TCP and forward it to serial port."""
        while self.running:
            try:
                data = self.tcp_client.recv(1024)
                if data:
                    if self.serial_conn:
                        self.serial_conn.write(data)
                        self.log_comm(data, ">>>")
            except (socket.timeout, socket.error) as e:
                self.log(f"TCP to Serial error: {e}")
                if self.auto_reconnect:
                    self.log("Attempting to reconnect...")
                    time.sleep(3)
                    self.try_connect_tcp_server()
                else:
                    self.stop()
                break

    def serial_to_tcp(self):
        """Receive data from serial port and forward it to TCP."""
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    self.tcp_client.sendall(data)
                    self.log_comm(data, "<<<")
            except (serial.SerialException, socket.error) as e:
                self.log(f"Serial to TCP error: {e}")
                if self.auto_reconnect:
                    self.log("Attempting to reconnect...")
                    time.sleep(3)
                    self.try_connect_serial_port()
                else:
                    self.stop()
                break

    def stop(self):
        self.running = False
        self.stop_tcp_client()
        self.stop_serial_port()
        # if self.tcp_to_serial_thread is not None and self.tcp_to_serial_thread.is_alive():
        #     self.tcp_to_serial_thread.join()
        # if self.serial_to_tcp_thread is not None and self.serial_to_tcp_thread.is_alive():
        #     self.serial_to_tcp_thread.join()
        self.heartbeat_event.set()  # 设置事件状态，使得心跳线程从等待中立即返回
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join()

    def stop_tcp_client(self):
        self.running = False
        self.stop_serial_port()
        if self.stop_function:
            self.stop_function()

    def stop_serial_port(self):
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None

    def send_heartbeat(self):
        if not self.enable_heartbeat or not self.heartbeat_data:
            return

        self.log("Heartbeat thread started.")
        data_to_send = binascii.unhexlify(self.heartbeat_data) if self.heart_hex else self.heartbeat_data.encode()

        if self.heartbeat_interval == 0:
            self.tcp_client.sendall(data_to_send)
            self.log_comm(data_to_send, "Heartbeat >>>")
        else:
            while self.running:
                try:
                    self.tcp_client.sendall(data_to_send)
                except socket.error as e:
                    print(f"send_heart_err:{e}")

                self.log_comm(data_to_send, "Heartbeat >>>")
                # 使用事件的wait方法等待，而不是直接睡眠
                self.heartbeat_event.wait(self.heartbeat_interval)
                self.heartbeat_event.clear()  # 清除事件状态以便下次等待
