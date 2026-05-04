import sys
import signal
import json

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtNetwork import QTcpSocket
from PySide6.QtWidgets import QApplication

class JSONObjectTCPReader(QObject):
    """TCP client that reads new line separated JSON objects with Qt."""

    tcp_stream_connected = Signal(bool)
    message_received = Signal(dict)

    def __init__(self, parent, host: str='127.0.0.1', port: int=49123, retry_interval: int=3000, debug_mode: bool=False):
        super().__init__(parent)
        self.debug_mode = debug_mode
        
        self.socket = QTcpSocket(self)
        self.host = host
        self.port = port
        self.retry_interval = retry_interval

        self.decoder = json.JSONDecoder()
        self.buffer = ""

        self.socket.connected.connect(self.on_connected)
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.readyRead.connect(self.on_ready_read)
        self.socket.errorOccurred.connect(self.on_error)

    def start(self):
        self.try_connect()

    def try_connect(self):
        if self.debug_mode: (f"[TCP-STREAM] Attempting to connect to {self.host}:{self.port}")
        self.socket.abort() # cancel ongoing connection attempts?

        self.socket.connectToHost(self.host, self.port)

    def schedule_retry(self):
        if self.debug_mode: (f"[TCP-STREAM] Retrying connection in {self.retry_interval} ms")
        QTimer.singleShot(self.retry_interval, self.try_connect)

    def on_connected(self):
        if self.debug_mode: print("[TCP-STREAM] Connected")
        self.tcp_stream_connected.emit(True)

    def on_disconnected(self):
        if self.debug_mode: print("[TCP-STREAM] Disconnected")
        self.tcp_stream_connected.emit(False)
        self.schedule_retry()

    def on_error(self):
        if self.debug_mode: print(f"[TCP-STREAM] Socket error: {self.socket.errorString()}")
        self.tcp_stream_connected.emit(False)
        self.schedule_retry()

    def on_ready_read(self):
        """
        Read TCP stream and incrementally decode JSON objects,
        instead of newline delimiters which don't seem to be implemented in the RL API.
        """

        data = bytes(self.socket.readAll()).decode('utf-8', errors='replace')
        if self.debug_mode: print(f"[TCP-STREAM] Raw chunk received: {data!r}")
        self.buffer += data
        self._process_buffer()

    def _process_buffer(self):
        """
        Try to decode as many JSON objects as possible from buffer.
        Keeps the rest if it contains anything.
        """

        while True:
            self.buffer = self.buffer.lstrip()

            if not self.buffer:
                return

            try:
                obj, idx = self.decoder.raw_decode(self.buffer)
            except json.JSONDecodeError:
                # If there is not a full JSON object, break the loop.
                return

            self.buffer = self.buffer[idx:] # Remove data that has been processed and emitted

            obj = self._deep_decode(obj) # recursively decodes nested json objects which apparently can be wrapped in quotes in the RL API. I dont think this is correct behavior

            if self.debug_mode: print(f"[TCP-STREAM] Parsed object: {obj}")

            self.message_received.emit(obj) 

    def _deep_decode(self, obj):
        if isinstance(obj, dict):
            return {k: self._deep_decode(v) for k, v in obj.items()}
        
        elif isinstance(obj, list):
            return [self._deep_decode(item) for item in obj]
        
        elif isinstance(obj, str):
            try:
                decoded = json.loads(obj)
                return self._deep_decode(decoded)
            except (json.JSONDecodeError, TypeError):
                return obj
        
        else:
            return obj



def main():
    app = QApplication(sys.argv)
    
    tcp = JSONObjectTCPReader(debug_mode=True)
    tcp.message_received.connect(lambda obj: print("[TCP-STREAM] Emitted object received:\n", obj))
    tcp.start()

    signal.signal(signal.SIGINT, signal.SIG_DFL) # This might not work, it is just to be able to stop the app from python console
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
