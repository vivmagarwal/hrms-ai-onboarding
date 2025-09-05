# HRMS AI-Powered Employee Onboarding System Requirements

## Introduction

### Problem Statement
Organizations struggle with manual, inconsistent, and time-consuming employee onboarding processes that often result in compliance issues, delayed access to tools, and poor new hire experiences.

### Solution Overview
A simple, free, web-based MVP that automates the entire employee onboarding workflow using AI agents (LangGraph) to orchestrate document signing, policy acknowledgment, quiz completion, system access provisioning, and onboarding scheduling - all without manual HR intervention. [Use context7 MCP server to access the latest documentations of LangGraph]

### Target Users
- **Primary**: HR administrators who initiate onboarding
- **Secondary**: New employees going through onboarding
- **Tertiary**: Anyone monitoring onboarding progress (managers, team leads)

## User Stories

1. **As an HR administrator**, I want to start onboarding with just basic employee info so that I can quickly initiate the process without extensive data entry.

2. **As an HR administrator**, I want the system to automatically handle the entire onboarding workflow so that I don't need to manually track each step.

3. **As a new employee**, I want to receive clear instructions and documents in the correct sequence so that I can complete my onboarding efficiently.

4. **As a manager**, I want to view the onboarding status of all employees in a dashboard so that I can track team readiness.

5. **As a system viewer**, I want to see real-time status updates so that I can monitor progress without needing to log in or authenticate.

## Core Requirements

### Functional Requirements

#### 1. Employee Management
1.1. Store employee information: Email, Name, Department/Role, Start Date
1.2. Display all employees in a table/grid view with status indicators
1.3. Show detailed status for each onboarding step per employee
1.4. No authentication required - fully open access

#### 2. Onboarding Workflow Orchestration
2.1. **Sequential Document Flow with Prerequisites**:
   - Company Policy → Signed → Quiz → Passed → Triggers NDA
   - NDA Policy → Signed → Quiz → Passed → Triggers Dev Guidelines
   - Dev Guidelines → Signed → Quiz → Passed → Triggers parallel actions

2.2. **Parallel Final Steps** (after Dev Guidelines quiz passed):
   - Send Slack access credentials
   - Send Jira access credentials  
   - Send onboarding call scheduling link

2.3. **AI Agent Orchestration**:
   - Use LangGraph to create agent workflow
   - Agents handle document sending, status tracking, quiz retries
   - Fully autonomous operation after HR initiates

#### 3. External Service Integration

3.1. **Document E-Sign Service** (https://doc-esign.onrender.com):
   - Send documents for signature (company_policy, nda_policy, dev_guidelines)
   - Track signature status via tracking IDs
   - Retrieve quiz IDs after signature completion
   - Submit quiz answers and track results
   - Handle immediate quiz retries on failure

3.2. **Email Service** (Webhook: https://hook.eu2.make.com/57dd2q56dzq8yis4qbkrlt5p473i7q5e):
   - Send all onboarding emails via webhook
   - AI-generated professional email content using OpenAI
   - Different email types:
     * Document signature requests
     * Quiz links and retry notifications
     * Slack/Jira access credentials
     * Calendly link for onboarding call

3.3. **AI Content Generation** (OpenAI):
   - API Key: [Set via environment variable OPENAI_API_KEY]
   - Model: gpt-4o-mini
   - Generate professional, context-aware email content

#### 4. Status Tracking
4.1. Track status for each step:
   - Not Started
   - Document Sent
   - Document Signed
   - Quiz Pending
   - Quiz Failed (retry sent)
   - Completed

4.2. Real-time status updates visible in dashboard
4.3. Visual indicators (✅ completed, ⏳ in progress, ❌ failed/retry, ⭕ not started)

### User Interface

#### Dashboard View
- **Layout**: Table/grid with fixed headers
- **Columns**:
  - Employee Name
  - Email
  - Department/Role
  - Start Date
  - Company Policy (status icon)
  - NDA Policy (status icon)
  - Dev Guidelines (status icon)
  - Slack Access (status icon)
  - Jira Access (status icon)
  - Onboarding Call (status icon)
  - Overall Progress (percentage or progress bar)
  - Actions (View Details / Start Onboarding)

#### Employee Details View
- Expandable row or modal showing:
  - Full employee information
  - Detailed status for each step with timestamps
  - Document tracking IDs
  - Quiz attempt history
  - Email send logs

#### Onboarding Initiation Form
- Simple form with fields:
  - Employee Email (required, validated)
  - Employee Name (required)
  - Department/Role (required, dropdown or text)
  - Start Date (required, date picker)
  - "Start Onboarding" button

### Edge Cases & Error Handling

1. **Quiz Failures**: Immediate retry with new email containing quiz link
2. **Email Delivery Failures**: Log error, display in UI, allow manual retry
3. **External Service Downtime**: 
   - Retry logic with exponential backoff
   - Display service status in dashboard
   - Allow manual intervention if needed
4. **Invalid Email Addresses**: Frontend validation + backend verification
5. **Duplicate Employees**: Check before creating new entry
6. **Incomplete Prerequisites**: Prevent advancing to next step
7. **Webhook Failures**: Log and queue for retry
8. **API Rate Limits**: Implement throttling and queuing

## Technical Architecture (per MVP Guidelines)

### Backend Structure
- Single `app.py` file with all FastAPI routes
- Pydantic models for validation
- TinyDB or JSON file for data persistence
- Async operations for external API calls
- Comprehensive API documentation in comments

### Frontend Structure
- Static HTML served from `/static/index.html`
- React via CDN for interactivity
- Tailwind CSS for styling
- No build process required

### File Structure
```
hrms/
├── app.py                 # All backend code
├── static/
│   ├── index.html        # Main UI
│   ├── css/             # Custom styles
│   └── js/              # Custom scripts
├── data/
│   └── employees.json    # Simple data storage
├── requirements.txt      # Pinned dependencies
├── .env.example         # Environment template
├── rest.rest            # VSCode REST Client tests
└── README.md            # Setup instructions
```

### API Endpoints
- `GET /` - Serve frontend
- `GET /api/employees` - List all employees with status
- `POST /api/employees` - Create new employee
- `GET /api/employees/{id}` - Get employee details
- `POST /api/onboarding/start` - Initiate onboarding for employee
- `GET /api/onboarding/status/{id}` - Get onboarding status
- `POST /api/webhook/document-status` - Receive document signing updates
- `POST /api/webhook/quiz-status` - Receive quiz completion updates

## Success Metrics
- Time from onboarding initiation to completion < 24 hours
- Zero manual interventions required for standard flow
- 100% document compliance achieved
- All system access provisioned before start date
- Dashboard loads in < 2 seconds

## Acceptance Criteria
1. ✅ HR can initiate onboarding with 4 fields
2. ✅ System automatically progresses through all steps
3. ✅ Prerequisites are enforced (no skipping steps)
4. ✅ Failed quizzes trigger immediate retries
5. ✅ Dashboard shows real-time status for all employees
6. ✅ No authentication required for access
7. ✅ All emails are AI-generated and professional
8. ✅ Parallel steps execute simultaneously after prerequisites
9. ✅ System handles external service failures gracefully
10. ✅ Complete audit trail available for each employee

## Out of Scope
- User authentication and role-based access
- Employee self-service portal
- Custom document templates
- Integration with HRIS systems
- Advanced reporting and analytics
- Mobile app
- Bulk employee import
- Custom quiz question configuration
- Integration with actual Slack/Jira APIs (using email simulation)
- Real calendar integration (using Calendly link only)

## Development Approach

### Phase 1: Backend Development
1. Set up FastAPI application structure
2. Create data models and storage
3. Implement employee CRUD operations
4. Build onboarding workflow with LangGraph
5. Integrate external services (doc-esign, email webhook)
6. Test all APIs with rest.rest file

### Phase 2: Frontend Development
1. Create dashboard with table view
2. Implement onboarding initiation form
3. Add real-time status updates
4. Build employee detail views
5. Apply professional UI with Tailwind CSS

### Phase 3: Testing & Deployment
1. End-to-end testing with Playwright
2. Create comprehensive README
3. Prepare for deployment (Render/Railway)

## Environment Configuration
```
# Email Webhook
EMAIL_WEBHOOK_URL=https://hook.eu2.make.com/57dd2q56dzq8yis4qbkrlt5p473i7q5e

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Document E-Sign Service
ESIGN_API_URL=https://doc-esign.onrender.com

# Calendly Link
CALENDLY_LINK=https://calendly.com/vivek-m-agarwal/30min
```

## Design System Requirements
- Follow design guide from `.claude/guides/designsystem-development-guide.md`
- Professional, clean interface optimized for data display
- Accessible with proper contrast and keyboard navigation
- Responsive design for desktop and tablet viewing
- Status indicators with clear visual hierarchy

## Additional Notes
- System operates completely autonomously after initiation
- All data is automatically cleared at midnight IST for privacy
- The doc-esign service is maintained by the same developer
- Quiz questions are generated from document content
- Unlimited quiz retries are allowed
- Email content is dynamically generated for personalization