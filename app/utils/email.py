
import random
import string
from typing import List
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
import os

def generate_otp(length=6):
    """Generate a random OTP."""
    return ''.join(random.choices(string.digits, k= length))

class Email:
    def __init__(self, user: dict, url: str, email: List[EmailStr]):
        self.name = user['username']
        self.sender = 'Codevo <admin@admin.com>'
        self.email = email
        self.url = url

    async def sendMail(self, subject, otp):
        # Define the config
        conf = ConnectionConfig(
            MAIL_USERNAME="chaty142@gmail.com",
            MAIL_PASSWORD="kdbjhrmsymddikjb",
            MAIL_FROM="chaty142@gmail.com",
            MAIL_PORT=587,
            MAIL_SERVER="smtp.gmail.com",
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )

        # Define the HTML content of the email
        html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{subject}</title>
            </head>
            <body>
                <p>Hello {self.name},</p>
                <p>Your verification code is: <strong>{otp}</strong></p>
                <p>Please use this code to verify your email address.</p>
                <p>If you did not request this verification code, you can safely ignore this email.</p>
                <p>Thank you!</p>
            </body>
            </html>
        """

        # Define the message options
        message = MessageSchema(
            subject=subject,
            recipients=self.email,
            body=html_content,
            subtype=MessageType.html
        )

        # Send the email
        fm = FastMail(conf)
        try:
            await fm.send_message(message)
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")
            raise

    async def sendVerificationCode(self, otp):
        # Generate OTP
        print(f"Generated OTP: {otp}")

        # Send email with OTP
        await self.sendMail('Your verification code (Valid for 10min)', otp)
