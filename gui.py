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

        self.print_var = tk.BooleanVar()
        print_log = bool(config['PrintLog'])
        self.print_var.set(print_log)
        self.hex_var = tk.BooleanVar()
        self.hex_var.set(bool(config['HexLog']))
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

    def add_log(self, message):
        """Add a message to the log box"""
        # Ensure the log update is performed on the main thread
        self.master.after(0, self.log_message, message)

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
        ip = self.server_ip.get()
        port = int(self.server_port.get())
        serial_port = self.serial_port.get()
        baud_rate = int(self.baud_rate.get())
        print_log = self.print_var.get()
        hex_log = self.hex_var.get()
        self.comm_manager = CommunicationManager(ip, port, serial_port, baud_rate, self.add_log, print_log, hex_log,
                                                 self.on_client_stop)
        self.comm_manager.start()
        self.is_communication_started = True
        self.config_manager.update_config(
            ServerIP=ip,
            ServerPort=str(port),
            SerialPort=serial_port,
            BaudRate=str(baud_rate),
            PrintLog=str(print_log),
            HexLog=str(hex_log)
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
