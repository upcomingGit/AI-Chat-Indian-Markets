# Backend Documentation

## Overview
The `backend` folder contains the Python-based backend for Saras – Your Personal AI Assistant for Indian Financial Markets. This backend is built using FastAPI and serves as the API layer for handling user queries, processing data, and interacting with financial data sources.

## Purpose
The backend provides:
- RESTful API endpoints for the frontend to interact with.
- Business logic for processing user queries about Indian financial markets and companies.
- Integration with data sources and LLMs (Large Language Models) for generating responses.

## Usage Details
- **Start the backend**: Run `pip install -r requirements.txt` to install dependencies, then start the server with `python -m app.main` or using a production server like `gunicorn`.
- **Configuration**: Environment variables (e.g., database connection strings, API keys) should be set in a `.env` file or via Azure App Service configuration.
- **Main entry point**: The application starts from `app/main.py`.

## Inputs
- **API Requests**: JSON payloads or query parameters sent from the frontend or other clients.
- **Environment Variables**: For configuration (e.g., DB credentials, API keys).

## Outputs
- **API Responses**: JSON responses containing financial data, analysis, or error messages.
- **Logs**: Console or file logs for debugging and monitoring.

## File Structure
- `app/` – Main FastAPI application and business logic.
- `requirements.txt` – Python dependencies.
- `start.sh` – Startup script for deployment (e.g., on Azure).

## Local Setup Instructions

To set up and run the backend on your local machine, follow these steps:

### 1. Prerequisites
- **Python 3.12+**: Download and install from [python.org](https://www.python.org/downloads/).
- **pip**: Comes bundled with Python. Check installation with:
  ```sh
  python --version
  pip --version
  ```

### 2. Install Dependencies
Navigate to the `backend` directory and run:
```sh
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the `backend` directory and add necessary variables (e.g., database connection strings, API keys).

### 4. Start the Development Server
Run:
```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Build/Deploy for Production
For Azure App Service or similar platforms, use the provided `start.sh` script:
```sh
sh start.sh
```

## LLM Router Logic (`app/llm_router.py`)

This module is responsible for routing user queries to the appropriate Large Language Model (LLM) or processing pipeline based on the nature of the question. The main goals and logic of `llm_router.py` are:

- **Intent Recognition**: Analyze incoming user queries to determine their intent (e.g., financial data lookup, general market analysis, company-specific questions).
- **Routing**: Based on the detected intent, route the query to the correct LLM, data service, or custom handler. This may involve:
  - Sending financial queries to a specialized financial data model or service.
  - Forwarding general queries to a general-purpose LLM (e.g., GPT-based model).
  - Handling fallback or error cases if the intent is unclear.
- **Preprocessing**: Optionally preprocess or enrich the query (e.g., extract company names, dates, or financial terms) before sending it to the LLM.
- **Postprocessing**: Format and return the LLM's response in a way that is suitable for the frontend, ensuring clarity and relevance.
- **Extensibility**: The router is designed to be extensible, allowing new types of queries or LLMs to be added as needed.

**What we are trying to do:**
- Provide intelligent, context-aware responses to user questions about Indian financial markets.
- Ensure that each query is handled by the most appropriate model or service for accurate and relevant answers.
- Maintain a modular and maintainable backend architecture for future enhancements.

---
For troubleshooting, refer to the FastAPI documentation or check the project README.
