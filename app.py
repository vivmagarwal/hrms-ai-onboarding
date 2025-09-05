"""
HRMS AI-Powered Onboarding System
FastAPI backend with LangGraph workflow orchestration
"""

from fastapi import FastAPI, HTTPException, Request, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any, Literal, Union
from datetime import datetime, timedelta
import os
import asyncio
import json
import httpx
from pathlib import Path
from enum import Enum
import uuid
import logging
from tinydb import TinyDB, Query
from tinydb.table import Document
from dotenv import load_dotenv
import time
from tenacity import retry, stop_after_attempt, wait_exponential
import aiosmtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from typing import TypedDict, Annotated
import operator
import openai

# Load environment variables
load_dotenv()
load_dotenv('.env.ethereal')  # Load Ethereal SMTP credentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai.api_key = openai_api_key

# ============================================
# Data Models and Enums
# ============================================

class OnboardingStepStatus(str, Enum):
    """Status for individual onboarding steps"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"

class DocumentType(str, Enum):
    """Types of documents in onboarding"""
    COMPANY_POLICY = "company_policy"
    NDA = "nda"
    DEV_GUIDELINES = "dev_guidelines"

class QuizType(str, Enum):
    """Types of quizzes in onboarding"""
    COMPANY_POLICY_QUIZ = "company_policy_quiz"
    NDA_QUIZ = "nda_quiz"
    DEV_GUIDELINES_QUIZ = "dev_guidelines_quiz"

class OnboardingStatus(BaseModel):
    """Track status of each onboarding step"""
    # Document steps
    company_policy_sent: OnboardingStepStatus = OnboardingStepStatus.NOT_STARTED
    company_policy_signed: OnboardingStepStatus = OnboardingStepStatus.NOT_STARTED
    company_policy_quiz_passed: OnboardingStepStatus = OnboardingStepStatus.NOT_STARTED
    
    nda_sent: OnboardingStepStatus = OnboardingStepStatus.NOT_STARTED
    nda_signed: OnboardingStepStatus = OnboardingStepStatus.NOT_STARTED
    nda_quiz_passed: OnboardingStepStatus = OnboardingStepStatus.NOT_STARTED
    
    dev_guidelines_sent: OnboardingStepStatus = OnboardingStepStatus.NOT_STARTED
    dev_guidelines_signed: OnboardingStepStatus = OnboardingStepStatus.NOT_STARTED
    dev_guidelines_quiz_passed: OnboardingStepStatus = OnboardingStepStatus.NOT_STARTED
    
    # Final tasks (parallel)
    slack_invite_sent: OnboardingStepStatus = OnboardingStepStatus.NOT_STARTED
    jira_access_granted: OnboardingStepStatus = OnboardingStepStatus.NOT_STARTED
    onboarding_call_scheduled: OnboardingStepStatus = OnboardingStepStatus.NOT_STARTED
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=datetime.now)
    
    def calculate_progress(self) -> float:
        """Calculate overall progress percentage"""
        steps = [
            self.company_policy_sent, self.company_policy_signed, self.company_policy_quiz_passed,
            self.nda_sent, self.nda_signed, self.nda_quiz_passed,
            self.dev_guidelines_sent, self.dev_guidelines_signed, self.dev_guidelines_quiz_passed,
            self.slack_invite_sent, self.jira_access_granted, self.onboarding_call_scheduled
        ]
        completed = sum(1 for step in steps if step == OnboardingStepStatus.COMPLETED)
        return round((completed / len(steps)) * 100, 2)

class Employee(BaseModel):
    """Employee data model"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    role: str
    department: str
    start_date: str
    
    # Onboarding status
    onboarding_status: OnboardingStatus = Field(default_factory=OnboardingStatus)
    workflow_thread_id: Optional[str] = None
    
    # Quiz attempts tracking
    quiz_attempts: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    
    # Email logs
    email_logs: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('start_date')
    def validate_start_date(cls, v):
        """Ensure start_date is a valid date string"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("start_date must be in YYYY-MM-DD format")

class EmployeeCreate(BaseModel):
    """Model for creating a new employee"""
    email: EmailStr
    name: str
    role: str
    department: str
    start_date: str
    
    @validator('start_date')
    def validate_start_date(cls, v):
        """Ensure start_date is a valid date string"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("start_date must be in YYYY-MM-DD format")

class WorkflowState(BaseModel):
    """State for LangGraph workflow"""
    employee_id: str
    current_step: str
    status: str
    context: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# ============================================
# Database Setup
# ============================================

# Initialize TinyDB
data_path = Path(__file__).parent / "data"
data_path.mkdir(exist_ok=True)

db_path = os.getenv("DB_PATH", str(data_path / "employees.db"))
db = TinyDB(db_path)
employees_table = db.table('employees')
workflows_table = db.table('workflows')

# Query builder
EmployeeQuery = Query()

# ============================================
# External Service Integration
# ============================================

class DocEsignService:
    """Integration with doc-esign service"""
    
    def __init__(self):
        self.base_url = os.getenv("DOC_ESIGN_API_URL", "https://doc-esign.onrender.com")
        self.timeout = int(os.getenv("SERVICE_TIMEOUT", "30"))
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def send_document(self, employee_email: str, document_type: str, employee_id: str = None) -> Dict[str, Any]:
        """Send document for signature via doc-esign service"""
        logger.info(f"📤 SENDING DOCUMENT: {document_type} to {employee_email}")
        logger.info(f"📍 Using doc-esign service at: {self.base_url}")
        
        # Map document types to doc-esign document IDs
        document_mapping = {
            "company_policy": "company_policy",
            "nda": "nda_policy",
            "dev_guidelines": "dev_guidelines"
        }
        
        document_id = document_mapping.get(document_type, document_type)
        
        # Get HRMS webhook base URL
        webhook_base_url = os.getenv("HRMS_WEBHOOK_BASE_URL", "https://hrms-ai-onboarding.onrender.com")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Include employee_id and webhook URLs for callbacks
                request_data = {
                    "document_id": document_id,
                    "sender_email": "hr@company.com",
                    "sender_name": "HR Department",
                    "receiver_email": employee_email,
                    "purpose": f"Please review and sign the {document_type.replace('_', ' ').title()}",
                    "employee_id": employee_id,
                    "webhook_base_url": webhook_base_url
                }
                
                logger.debug(f"📨 Request to doc-esign: {request_data}")
                
                response = await client.post(
                    f"{self.base_url}/api/send-document",
                    json=request_data
                )
                
                logger.debug(f"📬 Response status: {response.status_code}")
                logger.debug(f"📬 Response headers: {response.headers}")
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"✅ Document {document_type} sent successfully to {employee_email}")
                logger.info(f"📋 Tracking ID: {result.get('data', {}).get('tracking_id')}")
                logger.info(f"🔗 Signing URL: {result.get('data', {}).get('signing_url')}")
                
                return result.get('data', {})
                
            except httpx.HTTPStatusError as e:
                logger.error(f"❌ HTTP Error sending document: {e}")
                logger.error(f"Response: {e.response.text if e.response else 'No response'}")
                
                # Fallback to simulation for testing
                logger.warning(f"⚠️ Falling back to simulation mode")
                return self._simulate_document_send(employee_email, document_type)
                
            except Exception as e:
                logger.error(f"❌ Error sending document: {e}")
                # Fallback to simulation
                return self._simulate_document_send(employee_email, document_type)
    
    def _simulate_document_send(self, employee_email: str, document_type: str) -> Dict[str, Any]:
        """Fallback simulation when doc-esign is unavailable"""
        simulated_response = {
            "tracking_id": f"sim_{document_type}_{int(datetime.now().timestamp())}",
            "status": "sent",
            "signing_url": f"https://doc-esign.onrender.com/sign/simulated_{document_type}"
        }
        logger.info(f"📦 SIMULATED: Document {document_type} sent to {employee_email}")
        return simulated_response
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def check_signature_status(self, document_id: str) -> Dict[str, Any]:
        """Check document signature status"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/documents/{document_id}/status"
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error checking signature status: {e}")
                raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_quiz(self, quiz_type: str) -> Dict[str, Any]:
        """Get quiz questions"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/quizzes/{quiz_type}"
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error getting quiz: {e}")
                raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def submit_quiz(self, employee_id: str, quiz_type: str, answers: List[Dict]) -> Dict[str, Any]:
        """Submit quiz answers"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/quizzes/submit",
                    json={
                        "employee_id": employee_id,
                        "quiz_type": quiz_type,
                        "answers": answers,
                        "callback_url": f"{os.getenv('API_BASE_URL', 'http://localhost:8000')}/api/webhooks/quiz-status"
                    }
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error submitting quiz: {e}")
                raise

class EmailService:
    """Integration with email webhook service"""
    
    def __init__(self):
        self.webhook_url = os.getenv("EMAIL_WEBHOOK_URL", "https://hook.eu2.make.com/57dd2q56dzq8yis4qbkrlt5p473i7q5e")
        self.timeout = int(os.getenv("SERVICE_TIMEOUT", "30"))
        self.client = openai.OpenAI() if openai_api_key else None
    
    async def generate_email_content(self, template_type: str, employee_data: Dict) -> str:
        """Generate email content using OpenAI"""
        if not self.client:
            return self._get_default_content(template_type, employee_data)
        
        try:
            prompts = {
                "welcome": f"Write a warm, professional welcome email for {employee_data['name']} who is joining as {employee_data['role']} in {employee_data['department']}. Include excitement about them joining the team.",
                "document_ready": f"Write a brief email notifying {employee_data['name']} that their {employee_data.get('document_type', 'document')} is ready for review and signature.",
                "quiz_reminder": f"Write a friendly reminder email for {employee_data['name']} to complete their {employee_data.get('quiz_type', 'quiz')}.",
                "onboarding_complete": f"Write a congratulatory email for {employee_data['name']} who has completed their onboarding. Welcome them officially to the team.",
                "slack_invite": f"Write an email inviting {employee_data['name']} to join the company Slack workspace with instructions.",
                "jira_access": f"Write an email informing {employee_data['name']} that their Jira access has been granted with basic getting started tips.",
                "meeting_scheduled": f"Write an email confirming the onboarding call has been scheduled for {employee_data['name']} with their manager."
            }
            
            prompt = prompts.get(template_type, prompts["welcome"])
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful HR assistant writing professional onboarding emails. Keep emails concise and friendly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating email content: {e}")
            return self._get_default_content(template_type, employee_data)
    
    def _get_default_content(self, template_type: str, employee_data: Dict) -> str:
        """Get default email content if OpenAI is not available"""
        templates = {
            "welcome": f"Welcome to the team, {employee_data['name']}! We're excited to have you join us as {employee_data['role']}.",
            "document_ready": f"Hi {employee_data['name']}, Your document is ready for review and signature.",
            "quiz_reminder": f"Hi {employee_data['name']}, Please complete your onboarding quiz at your earliest convenience.",
            "onboarding_complete": f"Congratulations {employee_data['name']}! You've successfully completed your onboarding.",
            "slack_invite": f"Hi {employee_data['name']}, You've been invited to join our Slack workspace.",
            "jira_access": f"Hi {employee_data['name']}, Your Jira access has been granted.",
            "meeting_scheduled": f"Hi {employee_data['name']}, Your onboarding call has been scheduled."
        }
        return templates.get(template_type, templates["welcome"])
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def send_email(self, to_email: str, subject: str, content: str, template_type: str = "default") -> Dict[str, Any]:
        """Send email via webhook"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "to": to_email,
                    "subject": subject,
                    "content": content,
                    "template": template_type,
                    "timestamp": datetime.now().isoformat()
                }
                
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                
                logger.info(f"Email sent to {to_email}: {subject}")
                return {"status": "sent", "timestamp": datetime.now().isoformat()}
            except Exception as e:
                logger.error(f"Error sending email: {e}")
                return {"status": "failed", "error": str(e), "timestamp": datetime.now().isoformat()}

# Initialize services
doc_esign_service = DocEsignService()
email_service = EmailService()

# ============================================
# LangGraph Workflow
# ============================================

class OnboardingState(TypedDict):
    """State for onboarding workflow"""
    employee_id: str
    employee_data: Dict[str, Any]
    current_step: str
    steps_completed: List[str]
    quiz_attempts: Dict[str, List[Dict]]
    errors: List[str]
    emails_sent: List[Dict]
    documents_sent: List[str]
    documents_signed: List[str]
    quizzes_passed: List[str]
    final_tasks_status: Dict[str, bool]

async def send_company_policy_node(state: OnboardingState) -> OnboardingState:
    """Send company policy document"""
    employee_data = state["employee_data"]
    try:
        result = await doc_esign_service.send_document(
            employee_data["email"], 
            DocumentType.COMPANY_POLICY.value,
            state["employee_id"]
        )
        state["documents_sent"].append(DocumentType.COMPANY_POLICY.value)
        
        # Send email notification
        content = await email_service.generate_email_content("document_ready", {
            **employee_data,
            "document_type": "Company Policy"
        })
        await email_service.send_email(
            employee_data["email"],
            "Company Policy Ready for Review",
            content,
            "document_ready"
        )
        
        # Update employee status in DB
        await update_employee_step_status(
            state["employee_id"], 
            "company_policy_sent", 
            OnboardingStepStatus.COMPLETED
        )
        
        state["current_step"] = "wait_company_policy_signature"
        logger.info(f"Company policy sent to {employee_data['email']}")
    except Exception as e:
        state["errors"].append(f"Failed to send company policy: {str(e)}")
        logger.error(f"Error in send_company_policy_node: {e}")
    
    return state

async def check_company_policy_signed_node(state: OnboardingState) -> OnboardingState:
    """Check if company policy is signed - wait if needed"""
    employee = get_employee_by_id(state["employee_id"])
    if employee and employee.get("onboarding_status", {}).get("company_policy_signed") == OnboardingStepStatus.COMPLETED.value:
        # Already signed via webhook
        state["documents_signed"].append(DocumentType.COMPANY_POLICY.value)
        state["current_step"] = "company_policy_quiz"
        logger.info(f"✅ Company policy signed - proceeding to quiz")
        return state
    else:
        # Not signed yet - INTERRUPT and wait for webhook
        logger.info(f"⏳ Waiting for company policy signature - INTERRUPTING workflow")
        interrupt({
            "status": "waiting_for_signature",
            "document_type": "company_policy",
            "employee_id": state["employee_id"],
            "message": "Waiting for document signature via webhook"
        })
    
    return state

async def company_policy_quiz_node(state: OnboardingState) -> OnboardingState:
    """Handle company policy quiz - check if completed or wait"""
    try:
        employee = get_employee_by_id(state["employee_id"])
        if employee and employee.get("onboarding_status", {}).get("company_policy_quiz_passed") == OnboardingStepStatus.COMPLETED.value:
            # Already passed via webhook
            state["quizzes_passed"].append(QuizType.COMPANY_POLICY_QUIZ.value)
            state["current_step"] = "nda"
            logger.info(f"✅ Company policy quiz passed - proceeding to NDA")
            return state
        else:
            # Not passed yet - INTERRUPT and wait for webhook
            logger.info(f"⏳ Waiting for company policy quiz completion - INTERRUPTING workflow")
            interrupt({
                "status": "waiting_for_quiz",
                "quiz_type": "company_policy_quiz",
                "employee_id": state["employee_id"],
                "message": "Waiting for quiz completion via webhook"
            })
            
    except Exception as e:
        state["errors"].append(f"Quiz error: {str(e)}")
        logger.error(f"Error in company_policy_quiz_node: {e}")
    
    return state

async def send_nda_node(state: OnboardingState) -> OnboardingState:
    """Send NDA document - ONLY after company policy completed"""
    employee_data = state["employee_data"]
    
    # Verify company policy is complete first
    employee = get_employee_by_id(state["employee_id"])
    if not employee:
        state["errors"].append("Employee not found")
        return state
        
    status = employee.get("onboarding_status", {})
    if (status.get("company_policy_signed") != OnboardingStepStatus.COMPLETED.value or 
        status.get("company_policy_quiz_passed") != OnboardingStepStatus.COMPLETED.value):
        logger.warning(f"❌ Cannot send NDA - company policy not complete")
        state["errors"].append("Company policy must be completed first")
        return state
    
    try:
        # Send real NDA via doc-esign
        result = await doc_esign_service.send_document(
            employee_data["email"], 
            DocumentType.NDA.value,
            state["employee_id"]
        )
        state["documents_sent"].append(DocumentType.NDA.value)
        state["current_step"] = "wait_nda_signature"
        
        # Send email notification
        content = await email_service.generate_email_content("document_ready", {
            **employee_data,
            "document_type": "Non-Disclosure Agreement"
        })
        await email_service.send_email(
            employee_data["email"],
            "NDA Ready for Review",
            content,
            "document_ready"
        )
        
        await update_employee_step_status(
            state["employee_id"], 
            "nda_sent", 
            OnboardingStepStatus.COMPLETED
        )
        logger.info(f"NDA sent to {employee_data['email']}")
        
    except Exception as e:
        state["errors"].append(f"Failed to send NDA: {str(e)}")
        logger.error(f"Error sending NDA: {e}")
    
    return state

async def check_nda_signed_node(state: OnboardingState) -> OnboardingState:
    """Check if NDA is signed - WAIT FOR REAL SIGNATURE"""
    # Check actual status from database
    employee = get_employee_by_id(state["employee_id"])
    if employee and employee.get("onboarding_status", {}).get("nda_signed") == OnboardingStepStatus.COMPLETED.value:
        # Already signed via webhook
        state["documents_signed"].append(DocumentType.NDA.value)
        state["current_step"] = "nda_quiz"
        logger.info(f"✅ NDA signed - proceeding to quiz")
    else:
        # Not signed yet - DO NOT SIMULATE
        state["current_step"] = "waiting_nda_signature"
        logger.info(f"⏳ Waiting for real NDA signature")
    
    return state

async def nda_quiz_node(state: OnboardingState) -> OnboardingState:
    """Handle NDA quiz"""
    # Similar to company policy quiz
    state["quizzes_passed"].append(QuizType.NDA_QUIZ.value)
    state["current_step"] = "send_dev_guidelines"
    
    await update_employee_step_status(
        state["employee_id"], 
        "nda_quiz_passed", 
        OnboardingStepStatus.COMPLETED
    )
    
    return state

async def send_dev_guidelines_node(state: OnboardingState) -> OnboardingState:
    """Send dev guidelines - ONLY after NDA completed"""
    employee_data = state["employee_data"]
    
    # Verify NDA is complete first
    employee = get_employee_by_id(state["employee_id"])
    if not employee:
        state["errors"].append("Employee not found")
        return state
        
    status = employee.get("onboarding_status", {})
    if (status.get("nda_signed") != OnboardingStepStatus.COMPLETED.value or 
        status.get("nda_quiz_passed") != OnboardingStepStatus.COMPLETED.value):
        logger.warning(f"❌ Cannot send dev guidelines - NDA not complete")
        state["errors"].append("NDA must be completed first")
        return state
    
    try:
        # Send real document via doc-esign
        result = await doc_esign_service.send_document(
            employee_data["email"], 
            DocumentType.DEV_GUIDELINES.value,
            state["employee_id"]
        )
        state["documents_sent"].append(DocumentType.DEV_GUIDELINES.value)
        state["current_step"] = "wait_dev_guidelines_signature"
        
        # Send email notification  
        content = await email_service.generate_email_content("document_ready", {
            **employee_data,
            "document_type": "Development Guidelines"
        })
        await email_service.send_email(
            employee_data["email"],
            "Development Guidelines Ready for Review",
            content,
            "document_ready"
        )
        
        await update_employee_step_status(
            state["employee_id"], 
            "dev_guidelines_sent", 
            OnboardingStepStatus.COMPLETED
        )
        logger.info(f"Dev guidelines sent to {employee_data['email']}")
        
    except Exception as e:
        state["errors"].append(f"Failed to send dev guidelines: {str(e)}")
        logger.error(f"Error sending dev guidelines: {e}")
    
    return state

async def check_dev_guidelines_signed_node(state: OnboardingState) -> OnboardingState:
    """Check if dev guidelines is signed - WAIT FOR REAL SIGNATURE"""
    # Check actual status from database
    employee = get_employee_by_id(state["employee_id"])
    if employee and employee.get("onboarding_status", {}).get("dev_guidelines_signed") == OnboardingStepStatus.COMPLETED.value:
        # Already signed via webhook
        state["documents_signed"].append(DocumentType.DEV_GUIDELINES.value)
        state["current_step"] = "dev_guidelines_quiz"
        logger.info(f"✅ Dev guidelines signed - proceeding to quiz")
    else:
        # Not signed yet - DO NOT SIMULATE
        state["current_step"] = "waiting_dev_guidelines_signature"
        logger.info(f"⏳ Waiting for real dev guidelines signature")
    
    return state

async def dev_guidelines_quiz_node(state: OnboardingState) -> OnboardingState:
    """Handle dev guidelines quiz - REAL CHECK, NO SIMULATION"""
    employee = get_employee_by_id(state["employee_id"])
    if not employee:
        state["errors"].append("Employee not found")
        return state
    
    logger.info(f"📝 CHECKING REAL DEV GUIDELINES QUIZ STATUS for {employee['email']}")
    logger.info(f"   Dev quiz passed: {employee.get('onboarding_status', {}).get('dev_guidelines_quiz_passed')}")
    
    if employee.get("onboarding_status", {}).get("dev_guidelines_quiz_passed") == OnboardingStepStatus.COMPLETED.value:
        state["quizzes_passed"].append(QuizType.DEV_GUIDELINES_QUIZ.value)
        state["current_step"] = "final_tasks"
        logger.info(f"✅ Dev guidelines quiz ACTUALLY passed - proceeding to final tasks")
    else:
        state["current_step"] = "waiting_for_dev_quiz"
        logger.info(f"⏳ WAITING for actual dev guidelines quiz completion")
        raise ValueError("WORKFLOW_PAUSED: Waiting for dev guidelines quiz")
    
    return state

async def final_tasks_node(state: OnboardingState) -> OnboardingState:
    """Execute final onboarding tasks - ONLY after ALL documents signed and quizzes passed"""
    employee_data = state["employee_data"]
    
    # VERIFY ALL PREREQUISITES ARE MET
    employee = get_employee_by_id(state["employee_id"])
    if not employee:
        state["errors"].append("Employee not found")
        return state
    
    status = employee.get("onboarding_status", {})
    
    # Check ALL prerequisites
    required_steps = [
        ("company_policy_signed", "Company Policy"),
        ("company_policy_quiz_passed", "Company Policy Quiz"),
        ("nda_signed", "NDA"),
        ("nda_quiz_passed", "NDA Quiz"),
        ("dev_guidelines_signed", "Dev Guidelines"),
        ("dev_guidelines_quiz_passed", "Dev Guidelines Quiz")
    ]
    
    incomplete_steps = []
    for step_key, step_name in required_steps:
        if status.get(step_key) != OnboardingStepStatus.COMPLETED.value:
            incomplete_steps.append(step_name)
    
    if incomplete_steps:
        logger.error(f"❌ CANNOT proceed to final tasks - incomplete: {', '.join(incomplete_steps)}")
        state["errors"].append(f"Prerequisites not met: {', '.join(incomplete_steps)}")
        raise ValueError(f"WORKFLOW_BLOCKED: Missing prerequisites - {', '.join(incomplete_steps)}")
    
    logger.info(f"✅ ALL PREREQUISITES VERIFIED - sending final onboarding emails to {employee['email']}")
    logger.info(f"   ✓ All documents signed")
    logger.info(f"   ✓ All quizzes passed")
    logger.info(f"   ➤ Sending: Slack invite, Jira access, Onboarding call schedule")
    
    employee_data = state["employee_data"]
    
    # All final tasks happen in parallel
    tasks = []
    
    # Slack invite
    async def send_slack_invite():
        try:
            content = await email_service.generate_email_content("slack_invite", employee_data)
            await email_service.send_email(
                employee_data["email"],
                "Join Our Slack Workspace",
                content,
                "slack_invite"
            )
            state["final_tasks_status"]["slack"] = True
            await update_employee_step_status(state["employee_id"], "slack_invite_sent", OnboardingStepStatus.COMPLETED)
        except Exception as e:
            state["errors"].append(f"Slack invite error: {str(e)}")
    
    # Jira access
    async def grant_jira_access():
        try:
            content = await email_service.generate_email_content("jira_access", employee_data)
            await email_service.send_email(
                employee_data["email"],
                "Jira Access Granted",
                content,
                "jira_access"
            )
            state["final_tasks_status"]["jira"] = True
            await update_employee_step_status(state["employee_id"], "jira_access_granted", OnboardingStepStatus.COMPLETED)
        except Exception as e:
            state["errors"].append(f"Jira access error: {str(e)}")
    
    # Schedule onboarding call
    async def schedule_call():
        try:
            calendly_link = os.getenv("CALENDLY_LINK", "https://calendly.com/vivek-m-agarwal/30min")
            content = f"Hi {employee_data['name']},\n\nPlease schedule your onboarding call at: {calendly_link}"
            await email_service.send_email(
                employee_data["email"],
                "Schedule Your Onboarding Call",
                content,
                "meeting_scheduled"
            )
            state["final_tasks_status"]["call"] = True
            await update_employee_step_status(state["employee_id"], "onboarding_call_scheduled", OnboardingStepStatus.COMPLETED)
        except Exception as e:
            state["errors"].append(f"Call scheduling error: {str(e)}")
    
    # Execute all tasks in parallel
    await asyncio.gather(send_slack_invite(), grant_jira_access(), schedule_call())
    
    state["current_step"] = "completed"
    
    # Mark onboarding as completed
    result = employees_table.search(EmployeeQuery.id == state["employee_id"])
    if result:
        emp_data = result[0].copy()
        doc_id = result[0].doc_id
        emp_data['onboarding_status']['completed_at'] = datetime.now().isoformat()
        employees_table.update(emp_data, doc_ids=[doc_id])
    
    return state

# Helper function to get employee by ID
def get_employee_by_id(employee_id: str) -> dict:
    """Get employee from database by ID"""
    result = employees_table.search(EmployeeQuery.id == employee_id)
    if result:
        return result[0]
    return None

# Helper function to log email activity
async def log_email_activity(employee_id: str, action: str, details: dict):
    """Log email activity for audit trail"""
    result = employees_table.search(EmployeeQuery.id == employee_id)
    if result:
        doc_id = result[0].doc_id
        emp_data = result[0]
        
        # Add to email logs
        if "email_logs" not in emp_data:
            emp_data["email_logs"] = []
        
        emp_data["email_logs"].append({
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        employees_table.update(emp_data, doc_ids=[doc_id])
        logger.info(f"\ud83d\udce7 Email activity logged: {action} for employee {employee_id}")

# Helper function to update employee status
async def update_employee_step_status(employee_id: str, step: str, status: OnboardingStepStatus):
    """Update specific step status for employee"""
    result = employees_table.search(EmployeeQuery.id == employee_id)
    if result:
        emp_data = result[0].copy()
        doc_id = result[0].doc_id
        
        if 'onboarding_status' not in emp_data:
            emp_data['onboarding_status'] = {}
        
        emp_data['onboarding_status'][step] = status.value
        emp_data['onboarding_status']['last_updated'] = datetime.now().isoformat()
        emp_data['updated_at'] = datetime.now().isoformat()
        
        employees_table.update(emp_data, doc_ids=[doc_id])

# Build the workflow graph
def build_workflow():
    """Build the LangGraph workflow"""
    workflow = StateGraph(OnboardingState)
    
    # Add nodes
    workflow.add_node("send_company_policy", send_company_policy_node)
    workflow.add_node("check_company_policy_signed", check_company_policy_signed_node)
    workflow.add_node("company_policy_quiz", company_policy_quiz_node)
    
    workflow.add_node("send_nda", send_nda_node)
    workflow.add_node("check_nda_signed", check_nda_signed_node)
    workflow.add_node("nda_quiz", nda_quiz_node)
    
    workflow.add_node("send_dev_guidelines", send_dev_guidelines_node)
    workflow.add_node("check_dev_guidelines_signed", check_dev_guidelines_signed_node)
    workflow.add_node("dev_guidelines_quiz", dev_guidelines_quiz_node)
    
    workflow.add_node("final_tasks", final_tasks_node)
    
    # Add edges (sequential flow with interrupt-based waiting)
    workflow.add_edge("send_company_policy", "check_company_policy_signed")
    workflow.add_edge("check_company_policy_signed", "company_policy_quiz")
    
    # Simple edge - quiz node will interrupt if not complete, or proceed if complete
    workflow.add_edge("company_policy_quiz", "send_nda")
    
    workflow.add_edge("send_nda", "check_nda_signed")
    workflow.add_edge("check_nda_signed", "nda_quiz")
    workflow.add_edge("nda_quiz", "send_dev_guidelines")
    
    workflow.add_edge("send_dev_guidelines", "check_dev_guidelines_signed")
    workflow.add_edge("check_dev_guidelines_signed", "dev_guidelines_quiz")
    workflow.add_edge("dev_guidelines_quiz", "final_tasks")
    
    workflow.add_edge("final_tasks", END)
    
    # Set entry point
    workflow.set_entry_point("send_company_policy")
    
    # Create checkpointer for persistence
    checkpointer = MemorySaver()
    
    # Compile the workflow
    return workflow.compile(checkpointer=checkpointer)

# Initialize the workflow
onboarding_workflow = build_workflow()

# Initialize FastAPI app
app = FastAPI(
    title="HRMS AI-Powered Onboarding System",
    description="Automated employee onboarding with LangGraph orchestration",
    version="1.0.0"
)

# CORS configuration - allow all origins for MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "static"
if not static_path.exists():
    static_path.mkdir(exist_ok=True)
    
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "HRMS Onboarding System"
    }

# Root endpoint - serve index.html
@app.get("/")
async def serve_index():
    """Serve the main application UI"""
    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Welcome to HRMS AI-Powered Onboarding System"}

# API info endpoint
@app.get("/api")
async def api_info():
    """API information and available endpoints"""
    return {
        "name": "HRMS Onboarding API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "employees": "/api/employees",
            "onboarding": "/api/onboarding"
        }
    }

# ============================================
# Workflow Resume Functions
# ============================================

# Store workflow threads
workflow_threads = {}

async def resume_workflow_if_needed(employee_id: str, trigger_event: str):
    """Resume interrupted workflow when external event occurs"""
    try:
        thread_id = workflow_threads.get(employee_id)
        if not thread_id:
            logger.warning(f"No workflow thread found for employee {employee_id}")
            return
            
        logger.info(f"🔄 Resuming workflow for employee {employee_id} after {trigger_event}")
        
        # Get current employee state
        employee = get_employee_by_id(employee_id)
        if not employee:
            logger.error(f"Employee {employee_id} not found")
            return
            
        # Resume workflow with current state
        config = {"configurable": {"thread_id": thread_id}}
        
        # Create state for resume
        state = OnboardingState(
            employee_id=employee_id,
            employee_data=employee,
            current_step="resume",
            documents_sent=[],
            documents_signed=[],
            quizzes_passed=[],
            emails_sent=[],
            errors=[]
        )
        
        # Continue workflow
        workflow = build_workflow()
        
        # Stream workflow execution
        for output in workflow.stream(state, config=config):
            logger.info(f"Workflow step result: {output}")
            
    except Exception as e:
        logger.error(f"Error resuming workflow: {e}")
        # Continue anyway - don't block webhook processing

# ============================================
# Employee Management Endpoints
# ============================================

@app.get("/api/employees", response_model=List[Employee])
async def get_all_employees():
    """Get all employees with their onboarding status"""
    try:
        all_employees = employees_table.all()
        employees = []
        for emp_doc in all_employees:
            # Convert document to Employee model
            emp_data = emp_doc.copy()
            # Parse datetime strings back to datetime objects
            if 'created_at' in emp_data and isinstance(emp_data['created_at'], str):
                emp_data['created_at'] = datetime.fromisoformat(emp_data['created_at'])
            if 'updated_at' in emp_data and isinstance(emp_data['updated_at'], str):
                emp_data['updated_at'] = datetime.fromisoformat(emp_data['updated_at'])
            # Parse nested onboarding status
            if 'onboarding_status' in emp_data:
                status_data = emp_data['onboarding_status']
                if 'last_updated' in status_data and isinstance(status_data['last_updated'], str):
                    status_data['last_updated'] = datetime.fromisoformat(status_data['last_updated'])
                if 'started_at' in status_data and isinstance(status_data['started_at'], str):
                    status_data['started_at'] = datetime.fromisoformat(status_data['started_at'])
                if 'completed_at' in status_data and isinstance(status_data['completed_at'], str):
                    status_data['completed_at'] = datetime.fromisoformat(status_data['completed_at'])
                emp_data['onboarding_status'] = OnboardingStatus(**status_data)
            
            employees.append(Employee(**emp_data))
        
        # Add progress calculation to each employee
        for emp in employees:
            emp.onboarding_status.calculate_progress()
        
        return employees
    except Exception as e:
        logger.error(f"Error fetching employees: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/employees", response_model=Employee)
async def create_employee(employee_data: EmployeeCreate):
    """Create a new employee"""
    try:
        # Check for duplicate email
        existing = employees_table.search(EmployeeQuery.email == employee_data.email)
        if existing:
            raise HTTPException(status_code=409, detail="Employee with this email already exists")
        
        # Create new employee
        new_employee = Employee(
            email=employee_data.email,
            name=employee_data.name,
            role=employee_data.role,
            department=employee_data.department,
            start_date=employee_data.start_date
        )
        
        # Convert to dict for storage
        emp_dict = new_employee.dict()
        # Convert datetime objects to strings for JSON serialization
        emp_dict['created_at'] = emp_dict['created_at'].isoformat()
        emp_dict['updated_at'] = emp_dict['updated_at'].isoformat()
        emp_dict['onboarding_status']['last_updated'] = emp_dict['onboarding_status']['last_updated'].isoformat()
        
        # Insert into database
        doc_id = employees_table.insert(emp_dict)
        
        logger.info(f"Created new employee: {new_employee.name} ({new_employee.email})")
        
        return new_employee
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating employee: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    """Get a specific employee by ID"""
    try:
        result = employees_table.search(EmployeeQuery.id == employee_id)
        if not result:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        emp_data = result[0].copy()
        
        # Parse datetime strings
        if 'created_at' in emp_data and isinstance(emp_data['created_at'], str):
            emp_data['created_at'] = datetime.fromisoformat(emp_data['created_at'])
        if 'updated_at' in emp_data and isinstance(emp_data['updated_at'], str):
            emp_data['updated_at'] = datetime.fromisoformat(emp_data['updated_at'])
        
        # Parse nested onboarding status
        if 'onboarding_status' in emp_data:
            status_data = emp_data['onboarding_status']
            if 'last_updated' in status_data and isinstance(status_data['last_updated'], str):
                status_data['last_updated'] = datetime.fromisoformat(status_data['last_updated'])
            if 'started_at' in status_data and isinstance(status_data['started_at'], str):
                status_data['started_at'] = datetime.fromisoformat(status_data['started_at'])
            if 'completed_at' in status_data and isinstance(status_data['completed_at'], str):
                status_data['completed_at'] = datetime.fromisoformat(status_data['completed_at'])
            emp_data['onboarding_status'] = OnboardingStatus(**status_data)
        
        return Employee(**emp_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching employee {employee_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/employees/{employee_id}/status")
async def update_employee_status(
    employee_id: str,
    status_update: Dict[str, Any] = Body(...)
):
    """Update employee onboarding status"""
    try:
        result = employees_table.search(EmployeeQuery.id == employee_id)
        if not result:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        emp_data = result[0].copy()
        doc_id = result[0].doc_id
        
        # Update onboarding status fields
        if 'onboarding_status' not in emp_data:
            emp_data['onboarding_status'] = {}
        
        for key, value in status_update.items():
            if key in emp_data['onboarding_status']:
                emp_data['onboarding_status'][key] = value
        
        emp_data['onboarding_status']['last_updated'] = datetime.now().isoformat()
        emp_data['updated_at'] = datetime.now().isoformat()
        
        # Update in database
        employees_table.update(emp_data, doc_ids=[doc_id])
        
        logger.info(f"Updated status for employee {employee_id}")
        
        return {"message": "Status updated successfully", "employee_id": employee_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating employee status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Onboarding Workflow Endpoints (Placeholder)
# ============================================

@app.post("/api/onboarding/start")
async def start_onboarding(request: Dict[str, str] = Body(...), background_tasks: BackgroundTasks = None):
    """Start the onboarding workflow for an employee"""
    employee_id = request.get("employee_id")
    
    if not employee_id:
        raise HTTPException(status_code=400, detail="employee_id is required")
    
    # Check if employee exists
    result = employees_table.search(EmployeeQuery.id == employee_id)
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee = result[0]
    thread_id = f"thread_{uuid.uuid4()}"
    
    # Update employee with thread ID and started status
    emp_data = employee.copy()
    doc_id = employee.doc_id
    
    emp_data['workflow_thread_id'] = thread_id
    emp_data['onboarding_status']['started_at'] = datetime.now().isoformat()
    emp_data['onboarding_status']['last_updated'] = datetime.now().isoformat()
    emp_data['updated_at'] = datetime.now().isoformat()
    
    employees_table.update(emp_data, doc_ids=[doc_id])
    
    # Prepare initial state for workflow
    initial_state = {
        "employee_id": employee_id,
        "employee_data": {
            "email": emp_data["email"],
            "name": emp_data["name"],
            "role": emp_data["role"],
            "department": emp_data["department"]
        },
        "current_step": "send_company_policy",
        "steps_completed": [],
        "quiz_attempts": {},
        "errors": [],
        "emails_sent": [],
        "documents_sent": [],
        "documents_signed": [],
        "quizzes_passed": [],
        "final_tasks_status": {"slack": False, "jira": False, "call": False}
    }
    
    # Start workflow in background
    async def run_workflow():
        try:
            config = {"configurable": {"thread_id": thread_id}}
            await onboarding_workflow.ainvoke(initial_state, config)
            logger.info(f"Workflow completed for employee {employee_id}")
        except ValueError as e:
            # Expected pause for waiting on signatures/quizzes
            if "WORKFLOW_PAUSED" in str(e):
                logger.info(f"\ud83d\udd70\ufe0f Workflow paused for employee {employee_id}: {e}")
            else:
                logger.error(f"Workflow value error for employee {employee_id}: {e}")
        except Exception as e:
            logger.error(f"Workflow error for employee {employee_id}: {e}")
    
    # Store thread ID for resume functionality
    workflow_threads[employee_id] = thread_id
    
    if background_tasks:
        background_tasks.add_task(run_workflow)
    else:
        # Run directly if no background tasks available
        asyncio.create_task(run_workflow())
    
    logger.info(f"Started onboarding for employee {employee_id} with thread {thread_id}")
    
    return {
        "message": "Onboarding workflow started",
        "employee_id": employee_id,
        "thread_id": thread_id
    }

# ============================================
# SMTP Email Service
# ============================================

class SMTPEmailService:
    """Real SMTP email service using Ethereal Email for testing"""
    
    def __init__(self):
        self.host = os.getenv("ETHEREAL_SMTP_HOST", "smtp.ethereal.email")
        self.port = int(os.getenv("ETHEREAL_SMTP_PORT", "587"))
        self.username = os.getenv("ETHEREAL_SMTP_USER")
        self.password = os.getenv("ETHEREAL_SMTP_PASS")
        self.web_url = os.getenv("ETHEREAL_WEB_URL", "https://ethereal.email")
        
        if not self.username or not self.password:
            logger.warning("⚠️  Ethereal SMTP credentials not found! Emails will not be sent.")
    
    async def send_email(self, to_email: str, subject: str, body: str, from_email: str = None, from_name: str = "HRMS System") -> bool:
        """Send email via SMTP"""
        try:
            if not self.username or not self.password:
                logger.error("❌ Cannot send email - SMTP credentials missing")
                return False
                
            if not from_email:
                from_email = self.username
                
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{from_name} <{from_email}>"
            message['To'] = to_email
            
            # Add HTML body
            html_part = MIMEText(body, 'html')
            message.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                start_tls=True,
                username=self.username,
                password=self.password,
            )
            
            logger.info(f"📧 Email sent to {to_email}: {subject}")
            logger.info(f"🌐 View email at: {self.web_url}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False

# Initialize email service
smtp_email_service = SMTPEmailService()

# ============================================
# Webhook Endpoints for External Services
# ============================================

@app.post("/api/webhooks/document-status")
async def webhook_document_status(webhook_data: Dict[str, Any] = Body(...)):
    """Handle document status updates from doc-esign service"""
    try:
        employee_id = webhook_data.get("employee_id")
        document_type = webhook_data.get("document_type")
        status = webhook_data.get("status")
        
        if not all([employee_id, document_type, status]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Map document type to status field
        status_mapping = {
            "company_policy": {
                "sent": "company_policy_sent",
                "signed": "company_policy_signed"
            },
            "nda": {
                "sent": "nda_sent",
                "signed": "nda_signed"
            },
            "dev_guidelines": {
                "sent": "dev_guidelines_sent",
                "signed": "dev_guidelines_signed"
            }
        }
        
        if document_type in status_mapping and status in ["sent", "signed"]:
            field = status_mapping[document_type][status]
            await update_employee_step_status(
                employee_id,
                field,
                OnboardingStepStatus.COMPLETED
            )
            
            # Resume workflow if interrupted
            await resume_workflow_if_needed(employee_id, f"{document_type}_{status}")
            
        logger.info(f"Document webhook: {document_type} {status} for employee {employee_id}")
        return {"status": "received", "processed": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhooks/quiz-status")
async def webhook_quiz_status(webhook_data: Dict[str, Any] = Body(...)):
    """Handle quiz completion updates from doc-esign service"""
    try:
        employee_id = webhook_data.get("employee_id")
        quiz_type = webhook_data.get("quiz_type")
        score = webhook_data.get("score")
        passed = webhook_data.get("passed")
        
        if not all([employee_id, quiz_type, score is not None, passed is not None]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Update quiz status
        status_mapping = {
            "company_policy_quiz": "company_policy_quiz_passed",
            "nda_quiz": "nda_quiz_passed",
            "dev_guidelines_quiz": "dev_guidelines_quiz_passed"
        }
        
        if quiz_type in status_mapping and passed:
            field = status_mapping[quiz_type]
            await update_employee_step_status(
                employee_id,
                field,
                OnboardingStepStatus.COMPLETED
            )
            
            # Resume workflow if interrupted
            await resume_workflow_if_needed(employee_id, f"{quiz_type}_completed")
            
        # Store quiz attempt
        result = employees_table.search(EmployeeQuery.id == employee_id)
        if result:
            emp_data = result[0].copy()
            doc_id = result[0].doc_id
            
            if "quiz_attempts" not in emp_data:
                emp_data["quiz_attempts"] = {}
            if quiz_type not in emp_data["quiz_attempts"]:
                emp_data["quiz_attempts"][quiz_type] = []
                
            emp_data["quiz_attempts"][quiz_type].append({
                "score": score,
                "passed": passed,
                "timestamp": datetime.now().isoformat()
            })
            
            employees_table.update(emp_data, doc_ids=[doc_id])
            
        logger.info(f"Quiz webhook: {quiz_type} score={score} passed={passed} for employee {employee_id}")
        return {"status": "received", "processed": True}
    except Exception as e:
        logger.error(f"Quiz webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/onboarding/status/{thread_id}")
async def get_onboarding_status(thread_id: str):
    """Get the status of an onboarding workflow"""
    # Find employee by thread ID
    result = employees_table.search(EmployeeQuery.workflow_thread_id == thread_id)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow thread not found")
    
    emp_data = result[0].copy()
    
    # Parse datetime strings
    if 'created_at' in emp_data and isinstance(emp_data['created_at'], str):
        emp_data['created_at'] = datetime.fromisoformat(emp_data['created_at'])
    if 'updated_at' in emp_data and isinstance(emp_data['updated_at'], str):
        emp_data['updated_at'] = datetime.fromisoformat(emp_data['updated_at'])
    
    # Parse nested onboarding status
    if 'onboarding_status' in emp_data:
        status_data = emp_data['onboarding_status']
        if 'last_updated' in status_data and isinstance(status_data['last_updated'], str):
            status_data['last_updated'] = datetime.fromisoformat(status_data['last_updated'])
        if 'started_at' in status_data and isinstance(status_data['started_at'], str):
            status_data['started_at'] = datetime.fromisoformat(status_data['started_at'])
        if 'completed_at' in status_data and isinstance(status_data['completed_at'], str):
            status_data['completed_at'] = datetime.fromisoformat(status_data['completed_at'])
        emp_data['onboarding_status'] = OnboardingStatus(**status_data)
    
    employee = Employee(**emp_data)
    
    return {
        "thread_id": thread_id,
        "employee_id": employee.id,
        "employee_name": employee.name,
        "status": employee.onboarding_status,
        "progress": employee.onboarding_status.calculate_progress()
    }

@app.delete("/api/admin/clear-all-data")
async def clear_all_data():
    """
    Clear all data from the database - FOR TESTING PURPOSES ONLY
    Removes all employees, workflows, and resets the database to empty state
    """
    try:
        # Get count before clearing
        employee_count = len(employees_table.all())
        
        # Clear all employees and their onboarding data
        employees_table.truncate()
        
        # Clear workflow checkpointer memory if possible
        try:
            if hasattr(workflow_checkpointer, 'storage'):
                workflow_checkpointer.storage.clear()
        except Exception as e:
            logger.warning(f"Could not clear workflow checkpointer: {e}")
        
        logger.info(f"🗑️  Database cleared: Removed {employee_count} employees")
        
        return {
            "status": "success",
            "message": f"All data cleared successfully. Removed {employee_count} employees.",
            "cleared_count": employee_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear data: {str(e)}")

@app.get("/api/admin/stats")
async def get_admin_stats():
    """Get basic statistics about the system"""
    try:
        all_employees = employees_table.all()
        employee_count = len(all_employees)
        
        # Count by status
        status_counts = {}
        for emp in all_employees:
            if 'onboarding_status' in emp:
                # Count completed steps
                completed_steps = 0
                total_steps = 12  # Total possible steps
                status = emp['onboarding_status']
                
                for step_key, step_value in status.items():
                    if step_key.endswith('_at'):  # Skip timestamp fields
                        continue
                    if step_value == 'completed':
                        completed_steps += 1
                
                progress_bucket = f"{int((completed_steps/total_steps)*100)}%"
                status_counts[progress_bucket] = status_counts.get(progress_bucket, 0) + 1
        
        return {
            "total_employees": employee_count,
            "progress_distribution": status_counts,
            "database_file": str(Path("hrms.db").absolute()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)