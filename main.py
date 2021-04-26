from custom_smtp import Mail


def main():

    # Input section
    ip = input("Enter IP of mail server:")
    port = int(input("Enter port of mail server:"))
    timeout = input("Enter timeout period in seconds(Default:30):")
    from_mail = input("Enter name of sender:")
    to_mail = input("Enter name of receiver:")
    subject = input("Enter subject of mail:")
    body = input("Enter body of mail:")
    path = input("Enter path of attachment:")
    filename = input("Enter filename of attachment:")
    content_id = input("Enter name of attachment(default: image1):")

    # Handles default arguments
    if not timeout:
        timeout = 30
    if not content_id.isalpha():
        content_id = "image1"

    # Creates mail object synchronizes
    mail = Mail(ip, port, timeout)

    # Begins mail procedure
    mail.create_mail(from_mail, to_mail)

    # Writes input to mail
    mail.write_mail(from_mail, to_mail, subject, body, content_id)

    # Attaches file to email
    mail.create_attachment(path, filename, content_id)

    # Sends mail
    mail.send_mail()


# Runs main function
if __name__ == "__main__":
    main()
