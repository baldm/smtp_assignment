import base64
from socket import socket, AF_INET, SOCK_STREAM


class Mail():

    def __init__(self, ip, port, timeout):
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.settimeout(timeout)
        self.frontier = "--frontier\r\n".encode()

        print("Connecting to socket")
        self.client_socket.connect((ip, port))

        response = self.client_socket.recv(1024).decode()
        self.read_response(response)

        print("Sending EHLO")
        helo_command = 'EHLO mail.dtu.dk\r\n'

        self.client_socket.send(helo_command.encode())
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)
        print("Connection Established")

    def create_mail(self, from_mail, to_mail):
        print("Establishing mail")
        mail_from = f'MAIL FROM: <{from_mail}>\r\n'

        self.client_socket.send(mail_from.encode())
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)

        rcpt_to = f'RCPT TO: <{to_mail}>\r\n'
        self.client_socket.send(rcpt_to.encode())
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)

        print("Opening mail")

        self.client_socket.send('DATA\r\n'.encode())
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)

    def write_mail(self, from_name, to_name, subject, body, content_id=False):
        print("Writing mail")

        self.client_socket.send("MIME-Version: 1.0\r\n".encode())
        self.client_socket.send(f"FROM: {from_name}\r\n".encode())
        self.client_socket.send(f"TO: {to_name}\r\n".encode())
        self.client_socket.send(f"SUBJECT: {subject}\r\n".encode())
        self.client_socket.send(
            "Content-Type: multipart/related; boundary=frontier\r\n".encode())
        self.client_socket.send(self.frontier)

        self.client_socket.send(
            'Content-Type: text/html;charset="utf-8"\r\n'.encode())

        if content_id:
            self.client_socket.send(
                (f'\r \n <html>' +
                 '<body>' +
                 f'<h1>{subject}</h1>' +
                 f'{body}' +
                 '<div>' +
                 f'<img src="cid:{content_id}" alt="picture alt text" />' +
                 '</div>' +
                 '</body>' +
                 '</html>\r\n').encode())
        else:
            self.client_socket.send(
                (f'\r \n <html>' +
                 '<body>' +
                 f'<h1>{subject}</h1>' +
                 f'{body}' +
                 '</body>' +
                 '</html>\r\n').encode())

    def create_attachment(self, path, filename, content_id):
        print("Attaching file")

        with open(path, "rb") as image_file:
            attachment = base64.b64encode(image_file.read())

        self.client_socket.send(self.frontier)
        self.client_socket.send(
            f'Content-Type: image/jpeg; name={filename}\r\n'.encode())
        self.client_socket.send(
            f'Content-Disposition: attachment;filename="{filename}"\r\n'.encode())
        self.client_socket.send(
            "Content-Transfer-Encoding: base64\r\n".encode())
        self.client_socket.send(f"Content-ID: <{content_id}>\r\n".encode())

        self.client_socket.send("\r \n  ".encode()+attachment)
        self.client_socket.send(self.frontier)

        print("File attached")

    def send_mail(self):
        print("Sending mail")
        self.client_socket.send("--frontier--\r\n".encode())
        self.client_socket.send("\r\n.\r\n".encode())
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)

        print("Closing connection...")
        self.client_socket.send('QUIT\r\n'.encode())
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)
        print("Connection closed.")

    def read_response(self, response):
        response_code = response[:3]
        if response_code == "354":
            pass
        elif response_code[0] != "2":
            print("Something went wrong...")
            raise ConnectionError(response)
