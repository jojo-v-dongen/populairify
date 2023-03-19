import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader


def Send_Reset_Email(user_email, user_username, reset_password_url):
    # Set up your email and password
    try:
        email = ""
        password = ""

        # Set up the recipient email
        to_email = user_email

        # Load the email template file using Jinja2
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("reset_email.html")

        # Define the data for rendering the template
        data = {
            "reset_password_url": f"{reset_password_url}",
            "user": f"{user_username[0]}"
        }

        # Render the email template with the data
        email_body = template.render(data)

        # Create the message object and add the email content
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = to_email
        msg['Subject'] = "POPULAIRIFY: Reset Password"
        msg.attach(MIMEText(email_body, 'html'))

        # Set up the SMTP server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, to_email, msg.as_string())
        server.quit()
        return True
    
    except Exception as e:
        return e