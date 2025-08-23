# AI-Chat-Indian-Markets
A Gen AI project that provides a chat interface to input user queries and analyse financial data for Indian publicly-listed companies

There will be 2 folders: A react.js front-end, and a python backend

## Tools and Technologies Used

This project is built with a modern stack, combining a Python backend with a React frontend. Here’s a quick overview of the key technologies:

- **Backend (`FastAPI`)**:
  - **Framework**: `FastAPI` running on `Uvicorn` for development and `Gunicorn` for production.
  - **AI & LLM**:
  - **OpenAI GPT-5-mini**: Main LLM for chat, agent selection, and analysis tasks.
  - **fastmcp**: Used for Model Context Protocol (MCP) interactions and creating the Zerodha MCP Client
  - **Tooling**: `SlowAPI` for rate limiting, `Pydantic` for data validation, and `Pytest` for testing.

- **Frontend (`React`)**:
  - **Framework**: `React` with `react-scripts`.
  - **Styling**: `Tailwind CSS` for a utility-first design approach.
  - **API Communication**: `axios` for making HTTP requests to the backend.

- **Database**:
  - **Engine**: `PostgreSQL` (hosted on Azure) for persistent storage.
  - **Access**: Connected from Python using `psycopg2`.

- **Hosting (`Azure`)**:
  - **Platform**: The frontend and backend are deployed as separate `Azure App Service` web apps.
  - **Deployment**: Managed and deployed using the `Azure CLI`.