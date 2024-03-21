# Serial-TCP Bridge

The Serial-TCP Bridge is a Python application designed to facilitate the communication between serial ports and TCP/IP
networks. It enables devices connected via serial ports to communicate over TCP/IP networks, acting as a bridge. This
utility is particularly useful in scenarios where legacy devices lacking network interfaces need to be integrated into
modern networked environments.

## Features

- **TCP Server Settings**: Configure the IP address and port for the TCP server connection.
- **Serial Port Settings**: Select the serial port and set the baud rate for serial communication.
- **Heartbeat Mechanism**: Configure a periodic heartbeat message to ensure the TCP connection remains active.
- **Auto Reconnect**: Automatically attempts to reconnect in case of connection loss.
- **Logging**: Supports logging of the communication data and errors, both in hexadecimal and plaintext format.
- **GUI Interface**: A user-friendly graphical interface for easy configuration and monitoring.

## Installation

To use the Serial-TCP Bridge, you need Python installed on your system. This project is compatible with Python 3.6 or
later versions. You also need to install the following dependencies:

- `pySerial`: For serial communication.
- `Tkinter`: For the graphical user interface.

You can install the required packages using pip:

```
  pip install pyserial
```

## Usage

To start the application, run the `main.py` script:

This will open the GUI, where you can configure the TCP and serial settings, manage the heartbeat mechanism, and view
the communication logs.

## Configuration

The application uses a configuration file (`settings.ini`) to store the settings. You can edit this file directly or
configure the settings via the GUI.

Example configuration:

```
[DEFAULT]
ServerIP=127.0.0.1
ServerPort=9999
SerialPort=COM1
BaudRate=9600
PrintLog=False
HexLog=False
EnableHeartbeat=False
HeartbeatData=
HeartbeatInterval=0
HeartbeatHex=False
AutoReconnect=True
```

## Contributing

Contributions to the Serial-TCP Bridge project are welcome. Please feel free to fork the repository, make your changes,
and submit a pull request.

---

# Serial-TCP 桥

Serial-TCP 桥是一个 Python 应用程序，旨在促进串行端口与 TCP/IP 网络之间的通信。它使得通过串行端口连接的设备能够通过 TCP/IP
网络进行通信，充当桥梁。这个工具特别适用于需要将缺乏网络接口的旧设备集成到现代网络环境中的场景。

## 特性

- **TCP 服务器设置**：配置 TCP 服务器连接的 IP 地址和端口。
- **串行端口设置**：选择串行端口并设置串行通信的波特率。
- **心跳机制**：配置定期心跳消息以确保 TCP 连接保持活动状态。
- **自动重连**：在连接丢失的情况下自动尝试重新连接。
- **日志记录**：支持以十六进制和纯文本格式记录通信数据和错误。
- **图形用户界面**：友好的图形界面，便于配置和监控。

## 安装

要使用 Serial-TCP 桥，您需要在系统上安装 Python。该项目与 Python 3.6 或更高版本兼容。您还需要安装以下依赖项：

- `pySerial`：用于串行通信。
- `Tkinter`：用于图形用户界面。

您可以使用 pip 安装所需的包：

```
pip install pyserial
```

## 使用

要启动应用程序，请运行 `main.py` 脚本：

这将打开 GUI，您可以在其中配置 TCP 和串行设置，管理心跳机制，并查看通信日志。

## 配置

应用程序使用配置文件（`settings.ini`）存储设置。您可以直接编辑此文件或通过 GUI 配置设置。

配置示例：

```
[DEFAULT]
ServerIP=127.0.0.1
ServerPort=9999
SerialPort=COM1
BaudRate=9600
PrintLog=False
HexLog=False
EnableHeartbeat=False
HeartbeatData=
HeartbeatInterval=0
HeartbeatHex=False
AutoReconnect=True
```