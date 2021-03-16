import base64
from socket import socket, AF_INET, SOCK_STREAM

"""Mail class for demonstrating how a mail is built over smtp.
   Utilises MIME types for sending attachments and images
Raises:
    ConnectionError: When response from server is not 200 or input
"""


class Mail():

    def __init__(self, ip, port, timeout):
        """Generate mail object

        Args:
            ip (string): ip of mail host
            port (int): port of mail host
            timeout (int): timeout period in seconds
        """

        # Variable for later use
        self.frontier = "--frontier\r\n".encode()

        # Opens TCP socket and sets timeout
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.settimeout(timeout)

        # Connects socket and reads response
        print("Connecting to socket")
        self.client_socket.connect((ip, port))
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)

        # Sends EHLO command to get connection status
        print("Sending EHLO")
        helo_command = 'EHLO mail.dtu.dk\r\n'
        self.client_socket.send(helo_command.encode())
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)
        print("Connection Established")

    def create_mail(self, from_mail, to_mail):
        """Establishes mail and readies server for rest of mail     

        Args:
            from_mail (string): mail address of sender
            to_mail (string): mail address of receiver
        """

        # Sends MAIL FROM command and listens for response
        print("Establishing mail")
        mail_from = f'MAIL FROM: <{from_mail}>\r\n'
        self.client_socket.send(mail_from.encode())
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)

        # Sends RCPT TO command and listens for response
        rcpt_to = f'RCPT TO: <{to_mail}>\r\n'
        self.client_socket.send(rcpt_to.encode())
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)

        # Sends DATA command and opens server for full mail body
        print("Opening mail")
        self.client_socket.send('DATA\r\n'.encode())
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)

    def write_mail(self, from_name, to_name, subject, body, content_id=False):
        """For writing the contents of the mail

        Args:
            from_name (string): Name of sender
            to_name (string): Name of reciever
            subject (string): Subject line of mail
            body (string): Main body text of mail
            content_id (string, optional): content id of attachment. Defaults to False.
        """

        # Sends headers used in mail
        print("Writing mail")
        self.client_socket.send("MIME-Version: 1.0\r\n".encode())
        self.client_socket.send(f"FROM: {from_name}\r\n".encode())
        self.client_socket.send(f"TO: {to_name}\r\n".encode())
        self.client_socket.send(f"SUBJECT: {subject}\r\n".encode())
        self.client_socket.send(
            "Content-Type: multipart/related; boundary=frontier\r\n".encode())
        self.client_socket.send(self.frontier)

        # Changes content type to html
        self.client_socket.send(
            'Content-Type: text/html;charset="utf-8"\r\n'.encode())

        # Embeds image in mail if called with content id
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
        """Attaches file to mail

        Args:
            path (string): full path of file
            filename (string): name of file e.g. (image.jpg)
            content_id (string): id for image. Must be alphabetic characters
        """

        print("Attaching file")

        # Encodes attachment with base64
        with open(path, "rb") as image_file:
            attachment = base64.b64encode(image_file.read())

        # Sends headers for sending image attachment
        self.client_socket.send(self.frontier)
        self.client_socket.send(
            f'Content-Type: image/jpeg; name={filename}\r\n'.encode())
        self.client_socket.send(
            f'Content-Disposition: attachment;filename="{filename}"\r\n'.encode())
        self.client_socket.send(
            "Content-Transfer-Encoding: base64\r\n".encode())
        self.client_socket.send(f"Content-ID: <{content_id}>\r\n".encode())

        # Sends encoded attachment
        self.client_socket.send("\r \n  ".encode()+attachment)
        self.client_socket.send(self.frontier)
        print("File attached")

    def send_mail(self):
        """Finishes up mail and sends it
        """

        print("Sending mail")
        self.client_socket.send("--frontier--\r\n".encode())

        # Sends ending message to server and listens for response
        self.client_socket.send("\r\n.\r\n".encode())
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)

        # Closes TCP connection
        print("Closing connection...")
        self.client_socket.send('QUIT\r\n'.encode())
        response = self.client_socket.recv(1024).decode()
        self.read_response(response)
        print("Connection closed.")

    def read_response(self, response):
        """Helper function for reading server response

        Args:
            response (string): response from server

        Raises:
            ConnectionError: If the server throws an error
        """
        response_code = response[:3]
        if response_code == "354":
            pass
        elif response_code[0] != "2":
            print("Something went wrong...")
            raise ConnectionError(response)
