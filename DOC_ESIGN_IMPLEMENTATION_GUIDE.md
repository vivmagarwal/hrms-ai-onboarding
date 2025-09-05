# Doc-Esign Webhook Integration Implementation Guide

## CRITICAL ISSUE TO RESOLVE

**Problem:** The doc-esign service receives document requests from HRMS but does NOT send webhook callbacks when:
1. Documents are signed by users
2. Quizzes are completed by users

This causes HRMS onboarding workflows to get stuck waiting for notifications that never arrive.

**Solution:** Implement webhook callbacks from doc-esign to HRMS to notify when signatures and quizzes are completed.

---

## REPOSITORY CONTEXT

- **Repository:** https://github.com/vivmagarwal/doc-esign
- **Main file:** `app.py` (FastAPI application)
- **Framework:** FastAPI with TinyDB
- **Current Status:** Working for document signing and quiz taking, but missing webhook callbacks

---

## IMPLEMENTATION STEPS

### Step 1: Update Request Model to Accept Webhook Data

**File:** `app.py`
**Location:** Around line 108 in the `SendDocumentRequest` class

**CURRENT CODE:**
```python
class SendDocumentRequest(BaseModel):
    sender_email: EmailStr
    sender_name: str = Field(..., min_length=1, max_length=100)
    purpose: str = Field(..., min_length=1, max_length=500)
    receiver_email: EmailStr
    document_id: str = Field(..., pattern="^[a-z_]+$")
```

**CHANGE TO:**
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

### Step 2: Store Webhook Data in Database

**File:** `app.py`
**Location:** Around line 400-420 in the `/api/send-document` endpoint

**FIND this signature_record creation:**
```python
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

**ADD these two fields to the dictionary:**
```python
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
    # NEW WEBHOOK FIELDS - ADD THESE
    "employee_id": request.employee_id,
    "webhook_base_url": request.webhook_base_url
}
```

---

### Step 3: Add Webhook Callback Function

**File:** `app.py`
**Location:** After the `send_completion_email` function (around line 580)

**ADD this new function:**
```python
async def send_hrms_webhook(webhook_base_url: str, endpoint: str, payload: Dict[str, Any]) -> bool:
    """Send webhook callback to HRMS system"""
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

### Step 4: Send Webhook When Document is Signed

**File:** `app.py`
**Location:** In the `/api/submit-signature/{tracking_id}` endpoint (around line 480)

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

# Send quiz link email
await send_quiz_link_email(quiz_id, signature["receiver_email"], signature["document_title"])
```

**REPLACE with this (adds webhook callback):**
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

# Send quiz link email
await send_quiz_link_email(quiz_id, signature["receiver_email"], signature["document_title"])
```

---

### Step 5: Send Webhook When Quiz is Completed Successfully

**File:** `app.py`
**Location:** In the `/api/submit-quiz/{quiz_id}` endpoint (around line 570)

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

**REPLACE with this (adds webhook callback):**
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

## EXPECTED WEBHOOK PAYLOADS

### Document Signed Webhook
**Endpoint:** `{webhook_base_url}/api/webhooks/document-status`
**Method:** POST
**Payload:**
```json
{
    "employee_id": "8b266ce7-18d2-4b97-9656-170ed21d91d3",
    "document_type": "company_policy",
    "status": "signed",
    "timestamp": "2025-09-05T16:30:00.000Z"
}
```

### Quiz Completed Webhook
**Endpoint:** `{webhook_base_url}/api/webhooks/quiz-status`
**Method:** POST
**Payload:**
```json
{
    "employee_id": "8b266ce7-18d2-4b97-9656-170ed21d91d3",
    "quiz_type": "company_policy_quiz",
    "score": 3,
    "passed": true,
    "attempt_number": 1,
    "timestamp": "2025-09-05T16:35:00.000Z"
}
```

---

## TESTING THE IMPLEMENTATION

### Test Sequence:
1. **Deploy updated doc-esign** with webhook callbacks
2. **Create employee in HRMS** (POST /api/employees)
3. **Start onboarding workflow** (POST /api/onboarding/start)
4. **Sign document in doc-esign** 
5. **Verify HRMS receives document webhook** (check HRMS logs)
6. **Complete quiz in doc-esign**
7. **Verify HRMS receives quiz webhook** (check HRMS logs)
8. **Check employee status** shows progression through workflow

### Expected HRMS Log Messages:
```
Document webhook: company_policy signed for employee 8b266ce7-18d2-4b97-9656-170ed21d91d3
🔄 Resuming workflow for employee 8b266ce7-18d2-4b97-9656-170ed21d91d3 after company_policy_signed
Quiz webhook: company_policy_quiz score=3 passed=True for employee 8b266ce7-18d2-4b97-9656-170ed21d91d3
🔄 Resuming workflow for employee 8b266ce7-18d2-4b97-9656-170ed21d91d3 after company_policy_quiz_completed
```

---

## VALIDATION CHECKLIST

- [ ] Request model accepts `employee_id` and `webhook_base_url`
- [ ] Webhook data is stored in signature records
- [ ] Webhook function is implemented with error handling
- [ ] Document signing triggers webhook to HRMS
- [ ] Quiz completion triggers webhook to HRMS
- [ ] Webhooks include correct employee_id and payload format
- [ ] HRMS receives and processes webhooks successfully
- [ ] Workflow progresses through all steps to completion

---

## CRITICAL NOTES

1. **Always use `signature.get("field")` when accessing fields** to avoid KeyError if field doesn't exist
2. **Include comprehensive logging** for webhook attempts (success/failure)
3. **Handle webhook failures gracefully** - don't break the signing/quiz process if webhook fails
4. **Map document_id to correct quiz_type** using the provided mapping
5. **Test with real employee flow** to ensure end-to-end functionality

This implementation will fix the workflow progression issue and enable automatic advancement through the onboarding process! 🚀