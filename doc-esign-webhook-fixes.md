# Doc-Esign Webhook Integration Fixes

**CRITICAL:** These changes must be applied to the doc-esign service (https://github.com/vivmagarwal/doc-esign) to enable webhook callbacks to HRMS.

## Problem
Doc-esign service does NOT send webhook callbacks to HRMS when:
1. Documents are signed
2. Quizzes are completed

This causes HRMS workflows to remain stuck waiting for webhook notifications that never come.

## Solution Overview
1. Accept `employee_id` and `webhook_base_url` in document requests
2. Send webhook to HRMS when document is signed
3. Send webhook to HRMS when quiz is completed

---

## Change 1: Update SendDocumentRequest Model

**File:** `app.py` (around line 108)

**BEFORE:**
```python
class SendDocumentRequest(BaseModel):
    sender_email: EmailStr
    sender_name: str = Field(..., min_length=1, max_length=100)
    purpose: str = Field(..., min_length=1, max_length=500)
    receiver_email: EmailStr
    document_id: str = Field(..., pattern="^[a-z_]+$")
```

**AFTER:**
```python
class SendDocumentRequest(BaseModel):
    sender_email: EmailStr
    sender_name: str = Field(..., min_length=1, max_length=100)
    purpose: str = Field(..., min_length=1, max_length=500)
    receiver_email: EmailStr
    document_id: str = Field(..., pattern="^[a-z_]+$")
    employee_id: Optional[str] = Field(None, description="HRMS employee ID for webhook callbacks")
    webhook_base_url: Optional[str] = Field(None, description="Base URL for webhook callbacks to HRMS")
```

---

## Change 2: Update send_document endpoint to store webhook data

**File:** `app.py` (around line 400-420 in `/api/send-document`)

**FIND this code block in the signature_record:**
```python
    # Store in database
    signature_record = {
        "tracking_id": tracking_id,
        "document_id": request.document_id,
        "document_title": document["title"],
        "sender_email": request.sender_email,
        "sender_name": request.sender_name,
        "receiver_email": request.receiver_email,
        "purpose": request.purpose,
        "status": DocumentStatus.SENT,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "acknowledged": False,
        "quiz_id": None,
        "quiz_passed": False,
        "completed_at": None
    }
```

**ADD these fields:**
```python
    # Store in database
    signature_record = {
        "tracking_id": tracking_id,
        "document_id": request.document_id,
        "document_title": document["title"],
        "sender_email": request.sender_email,
        "sender_name": request.sender_name,
        "receiver_email": request.receiver_email,
        "purpose": request.purpose,
        "status": DocumentStatus.SENT,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "acknowledged": False,
        "quiz_id": None,
        "quiz_passed": False,
        "completed_at": None,
        # NEW WEBHOOK FIELDS
        "employee_id": request.employee_id,
        "webhook_base_url": request.webhook_base_url
    }
```

---

## Change 3: Add webhook callback function

**File:** `app.py` (add after the `send_completion_email` function, around line 580)

**ADD this new function:**
```python
async def send_hrms_webhook(webhook_base_url: str, endpoint: str, payload: Dict[str, Any]) -> bool:
    """Send webhook callback to HRMS"""
    if not webhook_base_url:
        logger.warning("No webhook base URL provided - skipping HRMS callback")
        return False
        
    try:
        webhook_url = f"{webhook_base_url.rstrip('/')}{endpoint}"
        logger.info(f"🔔 Sending HRMS webhook to: {webhook_url}")
        logger.info(f"📦 Webhook payload: {payload}")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"✅ HRMS webhook sent successfully: {endpoint}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to send HRMS webhook: {e}")
        return False
```

---

## Change 4: Send webhook when document is signed

**File:** `app.py` (in `/api/submit-signature/{tracking_id}` endpoint, around line 480)

**FIND this code block:**
```python
    # Update signature record
    signatures_table.update(
        {
            "acknowledged": submission.acknowledged,
            "acknowledgment_date": submission.date,
            "acknowledgment_location": submission.location,
            "signer_name": submission.name,
            "status": DocumentStatus.QUIZ_PENDING,
            "quiz_id": quiz_id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        SignatureQuery.tracking_id == tracking_id
    )
```

**ADD webhook callback AFTER the update:**
```python
    # Update signature record
    signatures_table.update(
        {
            "acknowledged": submission.acknowledged,
            "acknowledgment_date": submission.date,
            "acknowledgment_location": submission.location,
            "signer_name": submission.name,
            "status": DocumentStatus.QUIZ_PENDING,
            "quiz_id": quiz_id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        SignatureQuery.tracking_id == tracking_id
    )
    
    # Send webhook to HRMS about document signature
    if signature.get("webhook_base_url") and signature.get("employee_id"):
        await send_hrms_webhook(
            signature["webhook_base_url"],
            "/api/webhooks/document-status",
            {
                "employee_id": signature["employee_id"],
                "document_type": signature["document_id"],
                "status": "signed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
```

---

## Change 5: Send webhook when quiz is completed

**File:** `app.py` (in `/api/submit-quiz/{quiz_id}` endpoint, around line 570)

**FIND this code block where quiz is marked as passed:**
```python
    # Update signature status if passed
    if passed:
        SignatureQuery = TinyQuery()
        signature = signatures_table.get(SignatureQuery.quiz_id == quiz_id)
        
        signatures_table.update(
            {
                "status": DocumentStatus.COMPLETED,
                "quiz_passed": True,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            SignatureQuery.quiz_id == quiz_id
        )
        
        # Send completion emails
        await send_completion_email(
            signature["receiver_email"],
            signature["sender_email"],
            signature["document_title"],
            True,
            quiz_id
        )
```

**ADD webhook callback AFTER the completion emails:**
```python
    # Update signature status if passed
    if passed:
        SignatureQuery = TinyQuery()
        signature = signatures_table.get(SignatureQuery.quiz_id == quiz_id)
        
        signatures_table.update(
            {
                "status": DocumentStatus.COMPLETED,
                "quiz_passed": True,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            SignatureQuery.quiz_id == quiz_id
        )
        
        # Send completion emails
        await send_completion_email(
            signature["receiver_email"],
            signature["sender_email"],
            signature["document_title"],
            True,
            quiz_id
        )
        
        # Send webhook to HRMS about quiz completion
        if signature.get("webhook_base_url") and signature.get("employee_id"):
            # Map document_id to quiz_type for HRMS
            quiz_type_mapping = {
                "company_policy": "company_policy_quiz",
                "nda_policy": "nda_quiz", 
                "dev_guidelines": "dev_guidelines_quiz"
            }
            
            quiz_type = quiz_type_mapping.get(signature["document_id"], f"{signature['document_id']}_quiz")
            
            await send_hrms_webhook(
                signature["webhook_base_url"],
                "/api/webhooks/quiz-status",
                {
                    "employee_id": signature["employee_id"],
                    "quiz_type": quiz_type,
                    "score": correct_count,
                    "passed": True,
                    "attempt_number": quiz["attempts"] + 1,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
```

---

## Testing Instructions

1. **Apply all changes to doc-esign service**
2. **Deploy doc-esign with the changes**
3. **Test the complete workflow:**
   - Create employee in HRMS
   - Start onboarding workflow
   - Sign documents in doc-esign
   - Complete quizzes in doc-esign
   - Verify HRMS receives webhooks and workflow progresses

## Verification

After applying these changes:
- HRMS will send `employee_id` and `webhook_base_url` to doc-esign
- Doc-esign will callback to HRMS when documents are signed
- Doc-esign will callback to HRMS when quizzes are passed
- HRMS workflows will resume and progress to completion

**This fixes the root cause of the workflow progression issue!**