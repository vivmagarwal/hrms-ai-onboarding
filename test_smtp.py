#!/usr/bin/env python3
"""Test SMTP email service directly"""

import asyncio
from app import SMTPEmailService

async def test_email():
    """Test sending email via SMTP"""
    
    email_service = SMTPEmailService()
    
    success = await email_service.send_email(
        to_email="ydxvhgctqvcrsk4n@ethereal.email",
        subject="HRMS Test Email",
        body="""
        <html>
        <body>
            <h2>🎉 HRMS Email Test</h2>
            <p>This is a test email from the HRMS system.</p>
            <p><strong>Status:</strong> Email service working correctly!</p>
            <p>Check this email at: <a href="https://ethereal.email">https://ethereal.email</a></p>
        </body>
        </html>
        """,
        from_name="HRMS Test System"
    )
    
    if success:
        print("✅ Email sent successfully!")
        print("🌐 Check emails at: https://ethereal.email")
    else:
        print("❌ Email sending failed!")

if __name__ == "__main__":
    asyncio.run(test_email())