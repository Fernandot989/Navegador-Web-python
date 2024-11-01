from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
import socket

class WebBrowser(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(WebBrowser, self).__init__(*args, **kwargs)

        # Crear la ventana principal
        self.window = QWidget()
        self.window.setWindowTitle("Web Browser")

        # Crear el diseño principal
        self.layout = QVBoxLayout() 
        self.horizontal = QHBoxLayout()

        # Crear la barra de URL
        self.url_bar = QTextEdit()
        self.url_bar.setMaximumHeight(30)

        # Crear el botón "Go"
        self.go_btn = QPushButton("Go")
        self.go_btn.setMinimumHeight(30)

        # Añadir la barra de URL y el botón "Go" al diseño horizontal
        self.horizontal.addWidget(self.url_bar)
        self.horizontal.addWidget(self.go_btn)

        # Conectar el botón "Go" al método load_webpage
        self.go_btn.clicked.connect(self.load_webpage)

        # Añadir el diseño horizontal al diseño principal
        self.layout.addLayout(self.horizontal)

        # Crear el visor web
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)

        # Establecer el diseño principal en la ventana
        self.window.setLayout(self.layout)
        self.setCentralWidget(self.window)
        self.show()

    def load_webpage(self):
        # Obtener la URL de la barra de URL
        url = self.url_bar.toPlainText().strip()
        if url:
            # Obtener el contenido de la página web
            content = self.get_webpage(url)
            # Mostrar el contenido en el visor web
            self.web_view.setHtml(content)
        else:
            # Mostrar un mensaje de error si la URL es inválida
            self.web_view.setHtml("<html><body>Please enter a valid URL.</body></html>")

    def get_webpage(self, url):
        # Asegurarse de que la URL comience con http://
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        host, path = self.parse_url(url)

        # Crear una conexión de socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, 80))

        # Enviar la solicitud HTTP GET manualmente
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        print(f"Solicitud al servidor:\n{request}")
        client_socket.sendall(request.encode())

        # Recibir la respuesta
        response = b""
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            response += data

        client_socket.close()

        # Imprimir la respuesta completa en hexadecimal (para depuración)
        binary_response = ' '.join(format(byte, '08b') for byte in response)
        print(f"Respuesta del servidor en binario:\n{binary_response}")

        # Dividir los encabezados y el cuerpo
        header_data, body = response.split(b"\r\n\r\n", 1)
        headers = header_data.decode('iso-8859-1')  # Los encabezados HTTP usan codificación ISO-8859-1
        print(f"Respuesta del servidor en iso-8859-1:\n{headers}")
        print(f"Contenido del cuerpo:\n{body}")

        # Determinar la codificación a partir del encabezado Content-Type
        encoding = 'utf-8'  # Codificación predeterminada
        for line in headers.split('\r\n'):
            if line.lower().startswith('content-type:'):
                parts = line.split('charset=')
                if len(parts) > 1:
                    encoding = parts[1].strip()
                    break

        # Decodificar el cuerpo usando la codificación detectada
        decoded_content = body.decode(encoding, errors='replace')
        return decoded_content

    def parse_url(self, url):
        # Analizar la URL para obtener el host y el path
        if "://" in url:
            url = url.split("://")[1]
        if "/" in url:
            host, path = url.split("/", 1)
            path = "/" + path
        else:
            host = url
            path = "/"
        return host, path

# Ejemplo de uso
app = QApplication([])
window = WebBrowser()
app.exec_()