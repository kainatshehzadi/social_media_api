import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()  # Make sure you have a .env file loaded

def send_email_verification(email: str, otp: str):
    sender_email = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    print(f"[INFO] Preparing to send OTP to: {email}")
    print(f"[DEBUG] Using sender: {sender_email}, SMTP: {smtp_server}:{smtp_port}")

    subject = "Your OTP for Registration"
    body = f"Your OTP is: {otp}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, email, msg.as_string())
        print("[SUCCESS] OTP email sent.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send OTP: {e}")
        return False
