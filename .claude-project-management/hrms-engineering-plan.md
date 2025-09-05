# HRMS AI-Powered Onboarding Engineering Plan

## Usage
1. Read at session start
2. Update status after EACH task
3. Document discoveries inline
4. Keep sections current

## Workflow
1. Verify previous story = `completed`
2. Check ALL pre_implementation flags = `true` (never skip)
3. Execute task by task systematically
4. Update `task_notes` with context (critical - only source of truth)
5. Ensure working app after EVERY step

## Recommended MCP Servers
- **Playwright**: Verify UI changes and test user flows
- **Context7**: Get latest LangGraph and FastAPI documentation
- **Firecrawl**: Research external service documentation if needed

## Rules
- NO legacy fallback (unless explicit)
- NO backwards compatibility (unless explicit)
- Simple, robust, reliable, maintainable code
- After EACH feature: compile → test → verify
- Test external behavior (API calls, tools executed, results returned)
- Remove ALL mocks/simulations before completion
- Ask clarifying questions upfront
- Identify files to change per task

## Project Overview
An AI-powered employee onboarding system that automates the entire workflow using LangGraph agents to orchestrate document signing, quiz completion, and system access provisioning. The system operates autonomously after HR initiates onboarding with basic employee information, managing sequential prerequisites and parallel final tasks without manual intervention.

## Story Breakdown and Status

```yaml
stories:
  - story_id: "STORY-001"
    story_title: "Backend Infrastructure and Core Setup"
    story_description: "Set up FastAPI backend with basic project structure and dependencies"
    story_pre_implementation:
      requirements_understood: true
      context_gathered: true
      plan_read: true
      architecture_documented: true
      environment_ready: true
      tests_defined: true
    story_post_implementation:
      all_tasks_completed: true
      feature_working: true
      plan_updated: true
    story_implementation_status: "completed"
    tasks:
      - task_id: "TASK-001.1"
        task_title: "Initialize project structure and dependencies"
        task_description: "Create FastAPI project structure with all necessary directories and install core dependencies"
        task_acceptance_criteria:
          - "app.py file created with basic FastAPI setup"
          - "requirements.txt with all dependencies pinned"
          - ".env.example with all required variables"
          - "Directory structure matches MVP guidelines"
        task_pre_implementation:
          previous_task_done: true
        task_ready_to_complete:
          criteria_met: true
          code_working: true
          tests_passing: true
          integration_tested: true
          plan_updated: true
        task_implementation_status: "completed"
        task_implementation_notes: "Created app.py with basic FastAPI setup, requirements.txt with all dependencies, .env.example with required variables, and directory structure (static/, data/). All acceptance criteria met."
      
      - task_id: "TASK-001.2"
        task_title: "Set up FastAPI application with CORS and static file serving"
        task_description: "Configure FastAPI app with middleware, CORS settings, and static file mounting"
        task_acceptance_criteria:
          - "CORS configured for all origins (MVP requirement)"
          - "Static directory mounted at /static"
          - "Root endpoint serves index.html"
          - "Health check endpoint functional"
        task_pre_implementation:
          previous_task_done: true
        task_ready_to_complete:
          criteria_met: true
          code_working: true
          tests_passing: true
          integration_tested: true
          plan_updated: true
        task_implementation_status: "completed"
        task_implementation_notes: "Configured CORS for all origins, mounted static directory, root endpoint serves index.html, health check endpoint functional. Server tested and working on port 8000."
      
      - task_id: "TASK-001.3"
        task_title: "Create REST API test file"
        task_description: "Create rest.rest file with all API endpoint tests for VSCode REST Client"
        task_acceptance_criteria:
          - "rest.rest file created with all endpoints"
          - "Variables configured at top of file"
          - "Health check endpoint test works"
          - "File follows VSCode REST Client format"
        task_pre_implementation:
          previous_task_done: true
        task_ready_to_complete:
          criteria_met: true
          code_working: true
          tests_passing: true
          integration_tested: true
          plan_updated: true
        task_implementation_status: "completed"
        task_implementation_notes: "Created comprehensive rest.rest file with all planned endpoints, variables configured, health check tested successfully. File ready for VSCode REST Client usage."

  - story_id: "STORY-002"
    story_title: "Data Models and Storage Layer"
    story_description: "Implement data models with Pydantic and TinyDB/JSON storage for employee data persistence"
    story_pre_implementation:
      requirements_understood: true
      context_gathered: true
      plan_read: true
      architecture_documented: true
      environment_ready: true
      tests_defined: true
    story_post_implementation:
      all_tasks_completed: true
      feature_working: true
      plan_updated: true
    story_implementation_status: "completed"
    tasks:
      - task_id: "TASK-002.1"
        task_title: "Create Pydantic models for employee and onboarding data"
        task_description: "Define all data models for employees, onboarding status, and workflow state"
        task_acceptance_criteria:
          - "Employee model with all required fields"
          - "OnboardingStatus model with step tracking"
          - "WorkflowState model for LangGraph integration"
          - "Validation rules implemented"
        task_pre_implementation:
          previous_task_done: true
        task_ready_to_complete:
          criteria_met: true
          code_working: true
          tests_passing: true
          integration_tested: true
          plan_updated: true
        task_implementation_status: "completed"
        task_implementation_notes: "Created Employee, EmployeeCreate, OnboardingStatus, and WorkflowState models with full validation. Added enums for status types, document types, and quiz types. Includes progress calculation method."
      
      - task_id: "TASK-002.2"
        task_title: "Implement TinyDB storage layer"
        task_description: "Set up TinyDB for employee data persistence with CRUD operations"
        task_acceptance_criteria:
          - "TinyDB initialized with employees table"
          - "Database file created in data/ directory"
          - "Basic CRUD operations functional"
          - "Data persists between restarts"
        task_pre_implementation:
          previous_task_done: true
        task_ready_to_complete:
          criteria_met: true
          code_working: true
          tests_passing: true
          integration_tested: true
          plan_updated: true
        task_implementation_status: "completed"
        task_implementation_notes: "TinyDB configured with employees and workflows tables. Database file stored in data/employees.db. Query builder set up for efficient searches. Data persistence tested and verified."

  - story_id: "STORY-003"
    story_title: "Employee Management APIs"
    story_description: "Implement CRUD APIs for employee management with proper validation and error handling"
    story_pre_implementation:
      requirements_understood: true
      context_gathered: true
      plan_read: true
      architecture_documented: true
      environment_ready: true
      tests_defined: true
    story_post_implementation:
      all_tasks_completed: true
      feature_working: true
      plan_updated: true
    story_implementation_status: "completed"
    tasks:
      - task_id: "TASK-003.1"
        task_title: "Create employee CRUD endpoints"
        task_description: "Implement GET, POST endpoints for employee management"
        task_acceptance_criteria:
          - "GET /api/employees returns all employees with status"
          - "POST /api/employees creates new employee"
          - "GET /api/employees/{id} returns employee details"
          - "Duplicate email check implemented"
        task_pre_implementation:
          previous_task_done: true
        task_ready_to_complete:
          criteria_met: true
          code_working: true
          tests_passing: true
          integration_tested: true
          plan_updated: true
        task_implementation_status: "completed"
        task_implementation_notes: "All CRUD endpoints implemented and tested. Duplicate email validation working. Proper error handling with appropriate HTTP status codes. DateTime serialization handled correctly."
      
      - task_id: "TASK-003.2"
        task_title: "Add employee status tracking"
        task_description: "Implement status tracking for each onboarding step per employee"
        task_acceptance_criteria:
          - "Status fields for all 9 onboarding steps"
          - "Status enum with all possible states"
          - "Timestamp tracking for each step"
          - "Progress calculation implemented"
        task_pre_implementation:
          previous_task_done: true
        task_ready_to_complete:
          criteria_met: true
          code_working: true
          tests_passing: true
          integration_tested: true
          plan_updated: true
        task_implementation_status: "completed"
        task_implementation_notes: "OnboardingStatus model tracks all 12 steps (9 sequential + 3 parallel). Status enum with 6 states. Timestamps for started, completed, and last_updated. Progress calculation returns percentage. PUT endpoint for status updates."

  - story_id: "STORY-004"
    story_title: "External Service Integrations"
    story_description: "Integrate with doc-esign service, email webhook, and OpenAI for content generation"
    story_pre_implementation:
      requirements_understood: true
      context_gathered: true
      plan_read: true
      architecture_documented: true
      environment_ready: true
      tests_defined: true
    story_post_implementation:
      all_tasks_completed: true
      feature_working: true
      plan_updated: true
    story_implementation_status: "completed"
    tasks:
      - task_id: "TASK-004.1"
        task_title: "Implement doc-esign service integration"
        task_description: "Create client for doc-esign API with all required operations"
        task_acceptance_criteria:
          - "Send document for signature working"
          - "Check signature status functional"
          - "Submit signature acknowledgment working"
          - "Quiz operations (get/submit) functional"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-004.2"
        task_title: "Implement email service integration"
        task_description: "Create email sender using webhook with AI-generated content"
        task_acceptance_criteria:
          - "Email webhook integration working"
          - "OpenAI integration for content generation"
          - "Different email templates for each stage"
          - "Error handling for failed sends"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-004.3"
        task_title: "Add retry logic and error handling"
        task_description: "Implement exponential backoff and error handling for all external services"
        task_acceptance_criteria:
          - "Retry logic with exponential backoff"
          - "Service health checks implemented"
          - "Error logging and status updates"
          - "Fallback mechanisms in place"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""

  - story_id: "STORY-005"
    story_title: "LangGraph Workflow Engine"
    story_description: "Implement the core onboarding workflow using LangGraph with sequential and parallel execution"
    story_pre_implementation:
      requirements_understood: true
      context_gathered: true
      plan_read: true
      architecture_documented: true
      environment_ready: true
      tests_defined: true
    story_post_implementation:
      all_tasks_completed: true
      feature_working: true
      plan_updated: true
    story_implementation_status: "completed"
    tasks:
      - task_id: "TASK-005.1"
        task_title: "Set up LangGraph state and nodes"
        task_description: "Create LangGraph workflow with state schema and all required nodes"
        task_acceptance_criteria:
          - "OnboardingState schema defined"
          - "All 9 workflow nodes created"
          - "Node functions implement business logic"
          - "State persistence configured"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-005.2"
        task_title: "Implement sequential workflow with prerequisites"
        task_description: "Configure sequential edges for document → signature → quiz flow"
        task_acceptance_criteria:
          - "Sequential edges for company policy flow"
          - "Sequential edges for NDA flow"
          - "Sequential edges for dev guidelines flow"
          - "Prerequisites enforced between documents"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-005.3"
        task_title: "Implement conditional routing for quiz results"
        task_description: "Add conditional edges for quiz pass/fail scenarios with retry logic"
        task_acceptance_criteria:
          - "Quiz result evaluation logic"
          - "Pass routes to next document"
          - "Fail triggers immediate retry"
          - "Progress tracking updated correctly"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-005.4"
        task_title: "Implement parallel execution for final tasks"
        task_description: "Use Send API for parallel Slack, Jira, and onboarding call tasks"
        task_acceptance_criteria:
          - "Send API configured for parallel execution"
          - "All three final tasks execute simultaneously"
          - "State aggregation working correctly"
          - "Completion tracking accurate"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-005.5"
        task_title: "Add workflow persistence and checkpointing"
        task_description: "Configure SqliteSaver for workflow state persistence and recovery"
        task_acceptance_criteria:
          - "SqliteSaver configured and working"
          - "Checkpoints saved at each step"
          - "Workflow recoverable after failures"
          - "Thread-based state management"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""

  - story_id: "STORY-006"
    story_title: "Onboarding Orchestration APIs"
    story_description: "Create APIs to initiate and monitor the onboarding workflow"
    story_pre_implementation:
      requirements_understood: true
      context_gathered: true
      plan_read: true
      architecture_documented: true
      environment_ready: true
      tests_defined: true
    story_post_implementation:
      all_tasks_completed: true
      feature_working: true
      plan_updated: true
    story_implementation_status: "completed"
    implementation_notes: "Created /api/onboarding/start and /api/onboarding/status endpoints, webhook endpoints for document and quiz status. All tested with curl."
    tasks:
      - task_id: "TASK-006.1"
        task_title: "Create onboarding initiation endpoint"
        task_description: "Implement POST /api/onboarding/start to trigger LangGraph workflow"
        task_acceptance_criteria:
          - "Endpoint accepts employee ID"
          - "Validates employee exists"
          - "Triggers LangGraph workflow"
          - "Returns workflow thread ID"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-006.2"
        task_title: "Create onboarding status endpoint"
        task_description: "Implement GET /api/onboarding/status/{id} for real-time status"
        task_acceptance_criteria:
          - "Returns current workflow state"
          - "Shows all step statuses"
          - "Includes timestamps and progress"
          - "Updates reflect in real-time"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-006.3"
        task_title: "Implement webhook endpoints"
        task_description: "Create webhook endpoints for doc-esign status updates"
        task_acceptance_criteria:
          - "Document status webhook endpoint"
          - "Quiz status webhook endpoint"
          - "Updates trigger workflow continuation"
          - "Status reflected in database"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""

  - story_id: "STORY-007"
    story_title: "Frontend Dashboard Implementation"
    story_description: "Build the employee dashboard with real-time status updates using React via CDN"
    story_pre_implementation:
      requirements_understood: true
      context_gathered: true
      plan_read: true
      architecture_documented: true
      environment_ready: true
      tests_defined: true
    story_post_implementation:
      all_tasks_completed: true
      feature_working: true
      plan_updated: true
    story_implementation_status: "completed"
    implementation_notes: "Built React dashboard with employee table, detail modal, progress bars, status badges, and 5-second polling for real-time updates."
    tasks:
      - task_id: "TASK-007.1"
        task_title: "Create base HTML structure with React CDN"
        task_description: "Set up index.html with React, Tailwind CSS, and basic layout"
        task_acceptance_criteria:
          - "React 18 loaded via CDN"
          - "Tailwind CSS configured"
          - "Babel for JSX transformation"
          - "Base layout structure created"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-007.2"
        task_title: "Implement employee table component"
        task_description: "Create React component for employee table with status indicators"
        task_acceptance_criteria:
          - "Table displays all employees"
          - "Status icons for each step"
          - "Progress bar/percentage shown"
          - "Responsive design implemented"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-007.3"
        task_title: "Add real-time updates with polling"
        task_description: "Implement polling mechanism for real-time status updates"
        task_acceptance_criteria:
          - "Polling every 5 seconds"
          - "Status updates without refresh"
          - "Visual feedback for changes"
          - "Efficient update mechanism"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-007.4"
        task_title: "Create employee detail view"
        task_description: "Implement expandable row or modal for detailed employee status"
        task_acceptance_criteria:
          - "Shows all employee information"
          - "Detailed step status with timestamps"
          - "Quiz attempt history displayed"
          - "Email send logs visible"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""

  - story_id: "STORY-008"
    story_title: "Onboarding Initiation UI"
    story_description: "Build the form for HR to initiate employee onboarding"
    story_pre_implementation:
      requirements_understood: true
      context_gathered: true
      plan_read: true
      architecture_documented: true
      environment_ready: true
      tests_defined: true
    story_post_implementation:
      all_tasks_completed: true
      feature_working: true
      plan_updated: true
    story_implementation_status: "completed"
    implementation_notes: "Integrated EmployeeForm component with create and start onboarding functionality. Form includes validation, error handling, and API integration."
    tasks:
      - task_id: "TASK-008.1"
        task_title: "Create onboarding form component"
        task_description: "Build React form for new employee onboarding initiation"
        task_acceptance_criteria:
          - "Email field with validation"
          - "Name field required"
          - "Department/Role field"
          - "Start date picker"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-008.2"
        task_title: "Add form submission and API integration"
        task_description: "Connect form to backend APIs with proper error handling"
        task_acceptance_criteria:
          - "Form submits to /api/employees"
          - "Triggers onboarding workflow"
          - "Success/error feedback shown"
          - "Form resets after submission"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""

  - story_id: "STORY-009"
    story_title: "UI Polish and Design System"
    story_description: "Apply professional design with Tailwind CSS following design system guidelines"
    story_pre_implementation:
      requirements_understood: false
      context_gathered: false
      plan_read: false
      architecture_documented: false
      environment_ready: false
      tests_defined: false
    story_post_implementation:
      all_tasks_completed: false
      feature_working: false
      plan_updated: false
    story_implementation_status: "not_started"
    tasks:
      - task_id: "TASK-009.1"
        task_title: "Create design tokens and theme"
        task_description: "Implement design system with colors, typography, and spacing"
        task_acceptance_criteria:
          - "Color palette defined"
          - "Typography scale implemented"
          - "Spacing system consistent"
          - "Component styles unified"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-009.2"
        task_title: "Add loading states and animations"
        task_description: "Implement loading indicators and smooth transitions"
        task_acceptance_criteria:
          - "Loading states for all async operations"
          - "Skeleton loaders for table"
          - "Smooth transitions for status changes"
          - "Progress animations working"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-009.3"
        task_title: "Ensure accessibility compliance"
        task_description: "Implement ARIA labels, keyboard navigation, and contrast requirements"
        task_acceptance_criteria:
          - "ARIA labels on all interactive elements"
          - "Keyboard navigation functional"
          - "Color contrast meets WCAG AA"
          - "Screen reader compatible"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""

  - story_id: "STORY-010"
    story_title: "Testing and Documentation"
    story_description: "Complete end-to-end testing and create comprehensive documentation"
    story_pre_implementation:
      requirements_understood: false
      context_gathered: false
      plan_read: false
      architecture_documented: false
      environment_ready: false
      tests_defined: false
    story_post_implementation:
      all_tasks_completed: false
      feature_working: false
      plan_updated: false
    story_implementation_status: "not_started"
    tasks:
      - task_id: "TASK-010.1"
        task_title: "Complete API testing with rest.rest"
        task_description: "Test all API endpoints with various scenarios"
        task_acceptance_criteria:
          - "All endpoints tested"
          - "Error scenarios covered"
          - "Workflow sequences verified"
          - "External service mocks tested"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-010.2"
        task_title: "End-to-end testing with Playwright"
        task_description: "Create automated UI tests for complete onboarding flow"
        task_acceptance_criteria:
          - "Complete onboarding flow tested"
          - "Form submissions verified"
          - "Status updates confirmed"
          - "Error handling tested"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-010.3"
        task_title: "Create comprehensive README"
        task_description: "Document setup, configuration, and usage instructions"
        task_acceptance_criteria:
          - "Setup instructions complete"
          - "Environment configuration documented"
          - "API documentation included"
          - "Deployment guide provided"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""

  - story_id: "STORY-011"
    story_title: "Deployment Preparation"
    story_description: "Prepare application for deployment on Render or similar platform"
    story_pre_implementation:
      requirements_understood: false
      context_gathered: false
      plan_read: false
      architecture_documented: false
      environment_ready: false
      tests_defined: false
    story_post_implementation:
      all_tasks_completed: false
      feature_working: false
      plan_updated: false
    story_implementation_status: "not_started"
    tasks:
      - task_id: "TASK-011.1"
        task_title: "Create deployment configuration"
        task_description: "Set up run.py and deployment scripts for Render"
        task_acceptance_criteria:
          - "run.py with proper uvicorn configuration"
          - "PORT environment variable handling"
          - "Static file paths work in production"
          - "All dependencies in requirements.txt"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
      
      - task_id: "TASK-011.2"
        task_title: "Environment variable setup"
        task_description: "Configure all environment variables for production"
        task_acceptance_criteria:
          - ".env.example complete and accurate"
          - "All API keys documented"
          - "Service URLs configured"
          - "Production settings optimized"
        task_pre_implementation:
          previous_task_done: false
        task_ready_to_complete:
          criteria_met: false
          code_working: false
          tests_passing: false
          integration_tested: false
          plan_updated: false
        task_implementation_status: "not_started"
        task_implementation_notes: ""
```

## Architecture Decisions

**Decision 1**: Single-file FastAPI backend (app.py)
- Reasoning: MVP simplicity, easy to understand and maintain, no complex module imports
- Impact: All backend logic in one file, may need refactoring for production scale

**Decision 2**: LangGraph for workflow orchestration
- Reasoning: Built-in state management, checkpointing, parallel execution support, perfect for complex workflows
- Impact: Requires understanding of graph-based workflows but provides robust orchestration

**Decision 3**: TinyDB for data persistence
- Reasoning: No installation required, file-based, perfect for MVP, easy migration path to PostgreSQL
- Impact: Limited concurrent write performance, but sufficient for MVP scale

**Decision 4**: React via CDN without build process
- Reasoning: No build complexity, instant development, easy deployment, follows MVP guidelines
- Impact: Larger bundle size but acceptable for internal tool

**Decision 5**: Polling for real-time updates
- Reasoning: Simpler than WebSockets, sufficient for 5-second update intervals, no additional dependencies
- Impact: Slight delay in status updates but acceptable for onboarding workflow

**Decision 6**: Email via webhook instead of SMTP
- Reasoning: No email server configuration, works immediately, uses existing Make.com integration
- Impact: Dependency on external service but simplifies implementation

## Commands

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# Development
python app.py  # or uvicorn app:app --reload --port 8000

# Testing
# Use VSCode REST Client with rest.rest file
# Or use curl commands from rest.rest

# Linting (if added)
ruff check app.py
ruff format app.py

# Type checking (if added)
mypy app.py

# Build
# No build step required - static files served directly

# Deployment (Render)
python run.py  # Uses PORT environment variable
```

## Standards
- FastAPI async/await for all IO operations
- Pydantic models for all request/response validation
- TinyDB Query for all database operations
- React functional components with hooks
- Tailwind CSS utility classes only (no custom CSS)
- Status enums for consistency
- ISO 8601 timestamps for all dates
- camelCase for JavaScript, snake_case for Python
- Comprehensive error messages with status codes

## Git Flow
- Branch: feature/story-{id}
- Commit: "TASK-{id}: {description}"
- PR after story complete
- Squash merge to main

## Documentation
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React 18 Docs](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Doc-Esign API](https://doc-esign.onrender.com) (project's own service)
- [TinyDB Docs](https://tinydb.readthedocs.io/)

## Config Files
- requirements.txt: All Python dependencies with pinned versions
- .env.example: Environment variables template
- rest.rest: VSCode REST Client API tests
- README.md: Setup and usage instructions
- run.py: Production server startup script

## Directory Structure
```
hrms/
├── app.py                          # All backend code (FastAPI + LangGraph)
├── static/
│   ├── index.html                 # Main UI with React via CDN
│   ├── css/
│   │   └── custom.css            # Any custom styles if needed
│   └── js/
│       └── components.js         # React components if separated
├── data/
│   ├── employees.db              # TinyDB database file
│   └── langgraph.db             # LangGraph checkpoint storage
├── requirements.txt              # Python dependencies
├── .env.example                 # Environment template
├── .env                        # Local environment (git ignored)
├── run.py                      # Production server script
├── rest.rest                   # API tests for VSCode
├── README.md                   # Documentation
└── .claude-project-management/
    ├── hrms-raw-requirements.md      # Original requirements
    └── hrms-engineering-plan.md      # This file
```

## External Services
- **Doc-Esign API**: https://doc-esign.onrender.com
- **Email Webhook**: https://hook.eu2.make.com/57dd2q56dzq8yis4qbkrlt5p473i7q5e
- **OpenAI API**: For email content generation
- **Calendly**: https://calendly.com/vivek-m-agarwal/30min (link only)

## Key Implementation Notes
1. LangGraph workflow must handle both sequential prerequisites and parallel final tasks
2. Quiz failures must trigger immediate retries without blocking the workflow
3. All external service calls need retry logic with exponential backoff
4. Status updates must be reflected in real-time (5-second polling)
5. No authentication required - system is completely open access
6. Employee data persists in TinyDB, workflow state in LangGraph checkpoints
7. All emails are AI-generated using OpenAI for professional content
8. System must be fully autonomous after HR initiates onboarding