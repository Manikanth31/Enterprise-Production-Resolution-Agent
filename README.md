# Enterprise-Production-Resolution-Agent
GenAI-powered enterprise production incident investigation, root-cause analysis, and resolution recommendation agent.

## What this project does
This app investigates production incidents by reading order, invoice, payment, interface, and error-log data from SQLite, determines the likely root cause, and returns a recommended resolution.

## End-to-end workflow
1. A user enters an order ID and incident ID.
2. The agent queries the SQLite database for the related records.
3. The RCA layer inspects interface failures and error logs.
4. The project returns a summary, root-cause analysis, severity, and recommended action.
5. A FastAPI backend exposes the logic as an HTTP API.
6. A Streamlit front end provides a user-friendly dashboard for the same workflow.

## Run the backend API
```bash
cd /workspaces/Enterprise-Production-Resolution-Agent
python -m uvicorn app.api:app --host 0.0.0.0 --port 8000
```

## Run the frontend UI
```bash
cd /workspaces/Enterprise-Production-Resolution-Agent
streamlit run streamlit_app.py --server.port 8501
```

## Example CLI call
```bash
cd /workspaces/Enterprise-Production-Resolution-Agent
python -m app.main --order-id 5004 --incident-id INC-1001 --json
```

## Environment variables
Create a .env file or export variables before running the AI summary enhancement feature. The project accepts either a Gemini key or an OpenAI key.

```bash
# Gemini (recommended when using a Google AI Studio key)
export GEMINI_API_KEY="your_gemini_api_key_here"
export GEMINI_MODEL="gemini-1.5-flash"

# Optional fallback for OpenAI
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENAI_MODEL="gpt-4o-mini"
```

You can copy the template:
```bash
cp .env.example .env
```

## Demo order and incident IDs
The project is seeded with realistic enterprise incident data. The easiest way to explain the flow is to use one of the preloaded IDs below:

- Incident `INC-1001` -> Order `5004` -> delayed ERP interface timeout
- Incident `INC-1002` -> Order `5005` -> duplicate transaction / payment retry issue
- Incident `INC-1003` -> Order `5003` -> invoice reconciliation review
- Incident `INC-1004` -> Order `5002` -> payment status follow-up
- Incident `INC-1005` -> Order `5006` -> payment gateway token expiration
- Incident `INC-1006` -> Order `5007` -> inventory reservation timeout
- Incident `INC-1007` -> Order `5008` -> warehouse throttling / rate-limit event
- Order IDs live in the seed data at `database/seed_data.sql`
- Incident metadata lives in `data/incidents/*.json`

A good demo explanation is: "The user picks an incident ID from the catalog and the system matches it to the customer order that failed. We can identify the order by status, payment, interface error, and incident metadata in the SQLite records."

Example commands:

```bash
python -m app.main --order-id 5004 --incident-id INC-1001 --json
python -m app.main --order-id 5005 --incident-id INC-1002 --json
python -m app.main --order-id 5006 --incident-id INC-1005 --json
python -m app.main --order-id 5008 --incident-id INC-1007 --json
```

## API notes
The backend is available on http://localhost:8000 and the UI on http://localhost:8501 once started.
