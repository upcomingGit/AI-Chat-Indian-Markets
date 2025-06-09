#!/bin/bash

# Optional: Set working directory
cd /home/site/wwwroot

# Install dependencies
pip install -r requirements.txt

# Start the app (adjust path/module if needed)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --forwarded-allow-ips="*"
