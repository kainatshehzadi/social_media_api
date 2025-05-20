import secrets #secerect is use to generate secure token
import string
def generate_otp(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))