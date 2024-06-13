import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tomllib
import pprint

def send_email(subject, body, to_email):
    """Read outgoing email info from a TOML config file"""

    with open(".env.confg", "rb") as file_object:
        secret_dict = tomllib.load(file_object)
    #pprint.pprint(secret_dict)

     # Basic information
    host = secret_dict["outgoing_email_host"]
    port = secret_dict["outgoing_email_port"]
    from_email = secret_dict["outgoing_email_address"]
    from_password = secret_dict["outgoing_email_password"]
   
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")



