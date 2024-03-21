import tkinter as tk
from tkinter import ttk, scrolledtext
import serial.tools.list_ports
from communication_manager import CommunicationManager
from config_manager import ConfigManager


class SerialTCPGUI:
    def __init__(self, master):
        self.master = master
        master.title("Serial-TCP Bridge v1.0.0")

        self.config_manager = ConfigManager(filepath="settings.ini")
        self.config_manager.load_config()
        config = self.config_manager.get_config()

        # Get the list of system serial ports
        self.ports = [port.device for port in serial.tools.list_ports.comports()]
        self.comm_manager = None
        self.is_communication_started = False

        # TCP Settings
        self.tcp_frame = ttk.LabelFrame(master, text="TCP Settings")
        self.tcp_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(self.tcp_frame, text="Server IP:").grid(row=0, column=0, sticky="w")
        self.server_ip = ttk.Entry(self.tcp_frame)
        self.server_ip.grid(row=0, column=1)
        self.server_ip.insert(0, config['ServerIP'])

        ttk.Label(self.tcp_frame, text="Server Port:").grid(row=1, column=0, sticky="w")
        self.server_port = ttk.Entry(self.tcp_frame)
        self.server_port.grid(row=1, column=1)
        self.server_port.insert(0, config['ServerPort'])
        self.heartbeat_data = ttk.Entry(self.tcp_frame)
        # Auto reconnect

        self.auto_connect_check = tk.BooleanVar(value=self.str2bool(config.get('AutoReconnect', True)))
        ttk.Checkbutton(self.tcp_frame, text="Auto Reconnect",
                        variable=self.auto_connect_check,
                        command=self.change_auto_reconnect
                        ).grid(row=2, column=0, sticky="w")
        # Heartbeat Checkbutton
        self.heartbeat_check = tk.BooleanVar(value=self.str2bool(config.get('EnableHeartbeat', False)))
        ttk.Checkbutton(self.tcp_frame, text="Enable Heartbeat", variable=self.heartbeat_check,
                        command=self.toggle_heartbeat).grid(row=2, column=1, sticky="w")

        # 添加一个复选框用于选择心跳数据是否为十六进制
        self.heartbeat_hex_check = tk.BooleanVar(value=self.str2bool(config.get('HeartbeatHex', False)))
        self.heartbeat_hex_box = ttk.Checkbutton(self.tcp_frame, text="Heartbeat HEX",
                                                 variable=self.heartbeat_hex_check,
                                                 command=self.validate_heartbeat_data)

        self.heartbeat_hex_box.grid(row=2, column=2, sticky="w")

        self.heartbeat_data.bind('<KeyRelease>', self.validate_heartbeat_data)
        # 设置心跳内容
        ttk.Label(self.tcp_frame, text="Heartbeat Data:").grid(row=3, column=0, sticky="w")

        self.heartbeat_data.grid(row=3, column=1)
        self.heartbeat_interval = ttk.Entry(self.tcp_frame)
        ttk.Label(self.tcp_frame, text="Heartbeat Interval (0-3600s):").grid(row=4, column=0, sticky="w")
        self.heartbeat_interval.grid(row=4, column=1)
        ttk.Label(self.tcp_frame, text="0 for heartbeat at connection only").grid(row=5, column=1, sticky="w")

        self.heartbeat_data.insert(0, config['HeartbeatData'])
        self.heartbeat_interval.insert(0, config['HeartbeatInterval'])
        self.toggle_heartbeat()

        # Serial Settings
        self.serial_frame = ttk.LabelFrame(master, text="Serial Settings")
        self.serial_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(self.serial_frame, text="Port:").grid(row=0, column=0, sticky="w")
        self.serial_port = ttk.Combobox(self.serial_frame, values=self.ports)
        self.serial_port.grid(row=0, column=1)
        self.serial_port.set(config['SerialPort'])

        ttk.Label(self.serial_frame, text="Baud Rate:").grid(row=1, column=0, sticky="w")
        self.baud_rate = ttk.Combobox(self.serial_frame, values=[9600, 19200, 38400, 57600, 115200])
        self.baud_rate.grid(row=1, column=1)
        self.baud_rate.set(config['BaudRate'])

        # Print and HEX Options
        self.print_frame = ttk.LabelFrame(master, text="Options")
        self.print_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

        self.print_var = tk.BooleanVar(value=self.str2bool(config.get('PrintLog', False)))
        self.hex_var = tk.BooleanVar(value=self.str2bool(config.get('HexLog', False)))
        self.print_check = ttk.Checkbutton(self.print_frame, text="Print Data", variable=self.print_var,
                                           command=self.toggle_hex_option)
        self.print_check.grid(row=0, column=0, sticky="w")

        self.hex_check = ttk.Checkbutton(self.print_frame, text="HEX Format", variable=self.hex_var, state="disabled",
                                         command=self.on_hex_check)
        self.hex_check.grid(row=0, column=1, sticky="w")
        self.toggle_hex_option()
        # Start/Stop Button
        self.toggle_button = ttk.Button(master, text="Start", command=self.toggle_communication)
        self.toggle_button.grid(row=2, column=0, pady=10, sticky="ew", columnspan=2)

        # Log Text Box
        self.log_text = scrolledtext.ScrolledText(master, height=10)
        self.log_text.grid(row=3, column=0, columnspan=2, padx=10, sticky="ew")

    @staticmethod
    def str2bool(v):
        return str(v).lower() in ("yes", "true", "t", "1")

    def change_auto_reconnect(self):
        if self.comm_manager:
            self.comm_manager.set_auto_reconnect(self.auto_connect_check.get())

    def validate_heartbeat_data(self, event=None):
        """校验心跳数据是否为有效的十六进制字符串，并清理无效字符"""
        if self.heartbeat_hex_check.get():
            # 用户选择了十六进制数据输入
            content = self.heartbeat_data.get()
            hex_chars = "0123456789abcdefABCDEF"
            cleaned_content = ''.join(filter(lambda x: x in hex_chars, content))
            self.heartbeat_data.delete(0, tk.END)  # 清空输入框
            self.heartbeat_data.insert(0, cleaned_content)  # 插入校验后的内容

    def toggle_heartbeat(self):
        state = "normal" if self.heartbeat_check.get() else "disabled"
        self.heartbeat_data.config(state=state)
        self.heartbeat_interval.config(state=state)
        self.heartbeat_hex_box.config(state=state)
        # if not self.heartbeat_check.get():
        #     self.heartbeat_data.delete(0, tk.END)
        #     self.heartbeat_interval.delete(0, tk.END)

    def add_log(self, message):
        """Add a message to the log box, keep only the last 1000 lines in the GUI, and write older logs to a file."""
        # Ensure the log update is performed on the main thread
        self.master.after(0, self.log_message, message)

    def log_message(self, message):
        # 获得当前日志框中的所有内容，并按行分割
        current_logs = self.log_text.get('1.0', tk.END).splitlines()
        # 判断日志行数是否超过1000行
        if len(current_logs) > 1000:
            # 将旧的日志行写入文件
            with open("log_file.txt", "a") as log_file:
                for line in current_logs[:-1000]:
                    log_file.write(line + "\n")
            # 从日志框中删除旧的日志行，只保留最新的1000行
            self.log_text.delete('1.0', f'{len(current_logs) - 1000}.0')
        # 添加新的日志消息到日志框末尾
        self.log_text.insert(tk.END, message + "\n")
        # 自动滚动到日志框的底部
        self.log_text.see(tk.END)

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def on_hex_check(self):
        if self.comm_manager:
            self.comm_manager.set_hex_log(self.hex_var.get())

    def toggle_hex_option(self):
        if self.print_var.get():
            self.hex_check.config(state="normal")
        else:
            self.hex_check.config(state="disabled")
            self.hex_var.set(False)
        if self.comm_manager:
            self.comm_manager.set_print_log(self.print_var.get())

    def toggle_communication(self):
        if self.is_communication_started:
            self.stop_communication()
        else:
            self.start_communication()

    def start_communication(self):
        self.comm_manager = CommunicationManager(self.server_ip.get(),
                                                 int(self.server_port.get()),
                                                 self.serial_port.get(),
                                                 int(self.baud_rate.get()),
                                                 self.add_log,
                                                 self.print_var.get(),
                                                 self.hex_var.get(),
                                                 self.on_client_stop,
                                                 self.heartbeat_check.get(),
                                                 self.heartbeat_data.get(),
                                                 int(self.heartbeat_interval.get()),
                                                 self.heartbeat_hex_check.get(),
                                                 self.auto_connect_check.get()
                                                 )
        self.comm_manager.start()
        self.is_communication_started = True
        self.config_manager.update_config(
            ServerIP=self.server_ip.get(),
            ServerPort=str(self.server_port.get()),
            SerialPort=self.serial_port.get(),
            BaudRate=str(self.baud_rate.get()),
            PrintLog=str(self.print_var.get()),
            HexLog=str(self.hex_var.get()),
            EnableHeartbeat=str(self.heartbeat_check.get()),
            HeartbeatData=self.heartbeat_data.get(),
            HeartbeatInterval=str(self.heartbeat_interval.get()),
            HeartbeatHex=str(self.heartbeat_hex_check.get()),
            AutoReconnect=str(self.auto_connect_check.get())
        )
        self.log_message("Starting communication...")
        self.toggle_button["text"] = "Stop"

    def stop_communication(self):
        if self.comm_manager:
            self.comm_manager.stop()
            self.comm_manager = None

    def on_client_stop(self):
        self.log_message("Stopping communication...")
        self.toggle_button["text"] = "Start"
        self.is_communication_started = False


if __name__ == "__main__":
    root = tk.Tk()
    app = SerialTCPGUI(root)
    root.mainloop()
