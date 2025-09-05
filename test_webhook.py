#!/usr/bin/env python3
"""Test webhook endpoints manually"""

import httpx
import asyncio
import json

async def test_webhooks():
    base_url = "http://localhost:8000"
    
    # Test employee data
    employee_id = "8b266ce7-18d2-4b97-9656-170ed21d91d3"
    employee_email = "nikitavermajgd@gmail.com"
    
    async with httpx.AsyncClient() as client:
        # 1. Send document signed webhook
        print(f"📝 Sending document signed webhook for {employee_email}")
        doc_webhook = {
            "employee_id": employee_id,
            "document_type": "company_policy",
            "status": "signed"
        }
        
        response = await client.post(
            f"{base_url}/api/webhooks/document-status",
            json=doc_webhook
        )
        print(f"Document webhook response: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # 2. Send quiz completed webhook
        print(f"✅ Sending quiz completed webhook for {employee_email}")
        quiz_webhook = {
            "employee_id": employee_id,
            "quiz_type": "company_policy_quiz",
            "score": 3,
            "passed": True
        }
        
        response = await client.post(
            f"{base_url}/api/webhooks/quiz-status",
            json=quiz_webhook
        )
        print(f"Quiz webhook response: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_webhooks())