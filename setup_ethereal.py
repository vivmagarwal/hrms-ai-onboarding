#!/usr/bin/env python3
"""
Setup Ethereal Email credentials for testing
Based on Nodemailer's createTestAccount functionality
"""

import httpx
import json
import asyncio

async def create_ethereal_account():
    """Create an Ethereal test account via API"""
    try:
        # Ethereal's API endpoint for creating test accounts
        url = "https://api.nodemailer.com/user"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, 
                headers={"Content-Type": "application/json"},
                json={"requestor": "ethereal-hrms-test", "version": "1.0.0"}
            )
            
            if response.status_code == 200:
                account = response.json()
                print("✅ Ethereal Email Account Created Successfully!")
                print(f"📧 Email: {account.get('user')}")
                print(f"🔐 Password: {account.get('pass')}")
                print(f"🖥️  SMTP Host: {account.get('smtp', {}).get('host', 'smtp.ethereal.email')}")
                print(f"🔌 SMTP Port: {account.get('smtp', {}).get('port', 587)}")
                print(f"🔒 Security: STARTTLS")
                print(f"🌐 Web Interface: {account.get('web')}")
                
                # Save to .env file
                env_content = f"""
# Ethereal Email SMTP Configuration for Testing
ETHEREAL_SMTP_HOST={account.get('smtp', {}).get('host', 'smtp.ethereal.email')}
ETHEREAL_SMTP_PORT={account.get('smtp', {}).get('port', 587)}
ETHEREAL_SMTP_USER={account.get('user')}
ETHEREAL_SMTP_PASS={account.get('pass')}
ETHEREAL_WEB_URL={account.get('web')}
"""
                
                with open('.env.ethereal', 'w') as f:
                    f.write(env_content)
                    
                print("\n💾 Credentials saved to .env.ethereal")
                print("\n🧪 Test Configuration:")
                print(f"   - Use {account.get('user')} as test email address")
                print(f"   - Check emails at: {account.get('web')}")
                print(f"   - Account expires in 48 hours of inactivity")
                
                return account
            else:
                print(f"❌ Error creating account: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(create_ethereal_account())