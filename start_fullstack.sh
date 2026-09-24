#!/bin/bash
set -e

cd /workspaces/Enterprise-Production-Resolution-Agent

if ! lsof -i :8000 >/dev/null 2>&1; then
  nohup python -m uvicorn app.api:app --host 0.0.0.0 --port 8000 >/tmp/enterprise_agent_api.log 2>&1 &
fi

if ! lsof -i :8501 >/dev/null 2>&1; then
  nohup python -m streamlit run streamlit_app.py --server.port 8501 --server.headless true >/tmp/enterprise_agent_ui.log 2>&1 &
fi

echo "API: http://localhost:8000"
echo "UI: http://localhost:8501"
