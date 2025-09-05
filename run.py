#!/usr/bin/env python3
"""
HRMS AI-Powered Onboarding System - Production Runner
Starts the FastAPI application for production deployment
"""

import os
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (Render provides this)
    port = int(os.getenv("PORT", 8000))
    
    # Start the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )