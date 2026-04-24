#!/usr/bin/env python3
"""Entry point to start the FastAPI server"""

import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8888"))
    debug = os.getenv("DEBUG", "true").lower() == "true"

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
    )
