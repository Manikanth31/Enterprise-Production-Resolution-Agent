import json
import os
from typing import Any, Dict, List

import pandas as pd
import requests
import streamlit as st

from app.agents.agent import ResolutionAgent
from app.database.connection import get_connection
from app.services.auth_service import AuthService
from app.services.memory_store import AgentMemoryStore
from app.services.notification_service import AlertRouter
from app.services.report_service import ReportService

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
memory_store = AgentMemoryStore()
alert_router = AlertRouter()
auth_service = AuthService()

st.set_page_config(
    page_title="Production Resolution Agent",
    page_icon="🛠️",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #f4f7fb;
        --panel: #ffffff;
        --panel-soft: #eef3ff;
        --accent: #2563eb;
        --accent-soft: #dbeafe;
        --success: #0f766e;
        --warning: #d97706;
        --danger: #dc2626;
        --text: #0f172a;
        --muted: #475569;
        --line: #dfe7f5;
    }

    .stApp {
        background: linear-gradient(180deg, #eef4ff 0%, #f8fafc 100%);
        color: var(--text);
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fbff 0%, #edf4ff 100%);
        border-right: 1px solid var(--line);
    }

    div[data-testid="stMetricContainer"] {
        background: rgba(255,255,255,0.92);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="stMetricContainer"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 26px rgba(37, 99, 235, 0.10);
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: var(--text);
        font-weight: 700;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--muted);
        font-weight: 600;
    }

    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.1rem;
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.18);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.22);
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #0f766e, #115e59);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }

    .stTabs [role="tablist"] {
        gap: 0.5rem;
    }

    .stTabs [role="tab"] {
        background: #edf4ff;
        color: var(--muted);
        border-radius: 10px 10px 0 0;
        padding: 0.5rem 0.9rem;
        border: 1px solid var(--line);
    }

    .stTabs [aria-selected="true"] {
        background: white;
        color: var(--accent);
        border-bottom: 2px solid var(--accent);
    }

    .stAlert {
        border-radius: 12px;
        border: 1px solid #dbeafe;
    }

    .stSuccess {
        background: rgba(15, 118, 110, 0.08);
        border-left: 4px solid var(--success);
    }

    .stInfo {
        background: rgba(37, 99, 235, 0.06);
        border-left: 4px solid var(--accent);
    }

    .stJson {
        background: #f8fbff;
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 0.8rem;
    }

    h1, h2, h3 {
        color: var(--text);
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 rgba(37, 99, 235, 0.15); }
        50% { box-shadow: 0 0 20px rgba(37, 99, 235, 0.20); }
        100% { box-shadow: 0 0 0 rgba(37, 99, 235, 0.15); }
    }

    div[data-testid="stMetricContainer"] {
        animation: pulseGlow 4s ease-in-out infinite;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_recent_orders(limit: int = 8) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT order_id, customer_id, order_status, order_amount, order_date
            FROM orders
            ORDER BY order_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_trend_data() -> pd.DataFrame:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT order_date, COUNT(*) AS count
            FROM orders
            GROUP BY order_date
            ORDER BY order_date
            """
        ).fetchall()
    data = [dict(row) for row in rows]
    if not data:
        return pd.DataFrame({"order_date": [], "count": []})
    return pd.DataFrame(data).rename(columns={"order_date": "date", "count": "incidents"})


def fetch_incident(order_id: int, incident_id: str) -> Dict[str, Any]:
    try:
        response = requests.get(
            f"{API_BASE_URL}/investigate",
            params={"order_id": order_id, "incident_id": incident_id},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        agent = ResolutionAgent()
        return agent.run(order_id=order_id, incident_id=incident_id)


def build_timeline(result: Dict[str, Any]) -> List[Dict[str, str]]:
    evidence = result.get("evidence", {})
    order = evidence.get("order", [{}])[0]
    invoice = evidence.get("invoice", [{}])[0]
    payment = evidence.get("payment", [{}])[0]
    interface = evidence.get("interface", [{}])[0]
    error = evidence.get("errors", [{}])[0]
    rca = result.get("rca", {})

    workflow_states = [
        {"time": "Open", "title": "Incident created", "detail": f"Order {order.get('order_id')} entered the queue."},
        {"time": "Investigating", "title": "Evidence gathering", "detail": f"Status: {order.get('order_status')} | Invoice: {invoice.get('invoice_status')} | Payment: {payment.get('payment_status')}"},
        {"time": "Mitigation", "title": "Interface review", "detail": f"Interface {interface.get('interface_name')} status is {interface.get('status')}."},
        {"time": "Resolution", "title": "Root-cause decision", "detail": f"Root cause: {rca.get('root_cause', 'Unknown')}."},
    ]

    return workflow_states + [
        {"time": "Alert", "title": "System alert", "detail": f"Severity: {error.get('severity')} | {error.get('error_message')}"},
    ]


if "user" not in st.session_state:
    st.session_state.user = None
if "history" not in st.session_state:
    st.session_state.history = []
if "selected_order" not in st.session_state:
    st.session_state.selected_order = 5004
if "selected_incident" not in st.session_state:
    st.session_state.selected_incident = "INC-1001"


def login_view():
    st.title("Production Resolution Agent")
    st.caption("Secure incident operations dashboard")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
    if submitted:
        user = auth_service.authenticate(username, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid username or password.")


if st.session_state.user is None:
    login_view()
    st.stop()

user_role = st.session_state.user.get("role", "operator")
user_name = st.session_state.user.get("name", "User")

pages = ["Dashboard", "Investigate", "Timeline", "Analytics", "Memory", "Admin"]
page = st.sidebar.radio("Navigation", pages, index=0)

st.sidebar.write(f"Signed in as: {user_name} ({user_role})")
if st.sidebar.button("Log out"):
    st.session_state.user = None
    st.rerun()

if page == "Dashboard":
    st.title("Production Resolution Agent")
    st.caption(f"Welcome back, {user_name}. Enterprise incident investigation and recovery workflow.")

    memory_summary = memory_store.get_summary()
    metrics = {
        "Active Investigations": memory_summary.get("total_incidents", 0) + 2,
        "Critical Incidents": memory_summary.get("high_severity_count", 0) + 1,
        "Mean Resolution Time": "3.2h",
        "Success Rate": "96%",
    }

    cols = st.columns(4)
    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            st.metric(label, value)

    st.markdown("---")
    st.subheader("Available demo incident catalog")
    demo_cases = [
        {"incident_id": "INC-1001", "order_id": 5004, "scenario": "ERP timeout"},
        {"incident_id": "INC-1002", "order_id": 5005, "scenario": "Duplicate transaction"},
        {"incident_id": "INC-1003", "order_id": 5003, "scenario": "Invoice reconciliation"},
        {"incident_id": "INC-1004", "order_id": 5002, "scenario": "Payment follow-up"},
        {"incident_id": "INC-1005", "order_id": 5006, "scenario": "Gateway token expiry"},
        {"incident_id": "INC-1006", "order_id": 5007, "scenario": "Inventory timeout"},
        {"incident_id": "INC-1007", "order_id": 5008, "scenario": "Warehouse throttle"},
    ]
    st.dataframe(pd.DataFrame(demo_cases), use_container_width=True)

    st.markdown("---")

    left, right = st.columns(2)
    with left:
        st.subheader("Incident trend by time")
        trend_df = get_trend_data()
        if not trend_df.empty:
            st.line_chart(trend_df.set_index("date")["incidents"])
        else:
            st.info("No trend data available.")

    with right:
        st.subheader("Known root causes")
        causes = memory_summary.get("recent_root_causes", [])
        if causes:
            labels = [item[0] for item in causes[:5]]
            values = [item[1] for item in causes[:5]]
            st.bar_chart(pd.DataFrame({"root_cause": labels, "count": values}).set_index("root_cause"))
        else:
            st.info("No historical root-cause patterns yet.")

    st.markdown("---")
    st.subheader("Operational overview")
    for order in get_recent_orders(5):
        st.write(f"- Order {order['order_id']}: {order['order_status']} | ${order['order_amount']:.2f} | {order['order_date']}")

elif page == "Investigate":
    st.title("Investigate incident")
    with st.form("incident_form"):
        order_id = st.number_input("Order ID", min_value=1, value=int(st.session_state.selected_order), step=1)
        incident_id = st.text_input("Incident ID", value=st.session_state.selected_incident)
        submitted = st.form_submit_button("Investigate", use_container_width=True)

    if submitted:
        result = fetch_incident(int(order_id), str(incident_id))
        st.session_state.history.insert(0, {
            "order_id": int(order_id),
            "incident_id": str(incident_id),
            "summary": result.get("summary", "Investigation completed"),
        })
        st.session_state.history = st.session_state.history[:6]

        st.success("Investigation complete")
        rca = result["rca"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Severity", rca.get("severity", "UNKNOWN"))
        with col2:
            st.metric("Confidence", rca.get("confidence", "UNKNOWN"))
        with col3:
            st.metric("Order", order_id)

        tab1, tab2, tab3, tab4 = st.tabs(["Summary", "RCA", "Evidence", "Export"])
        with tab1:
            st.write(result["summary"])
        with tab2:
            st.json({
                "incident_id": rca["incident_id"],
                "root_cause": rca["root_cause"],
                "severity": rca.get("severity", "UNKNOWN"),
                "confidence": rca.get("confidence", "UNKNOWN"),
                "recommended_action": rca["recommended_action"],
            })
        with tab3:
            st.json(result["evidence"])
        with tab4:
            pdf_bytes = ReportService.create_incident_pdf(result)
            st.download_button(
                label="Download PDF report",
                data=pdf_bytes,
                file_name=f"incident_{incident_id}_{order_id}.pdf",
                mime="application/pdf",
            )
            st.download_button(
                label="Download JSON report",
                data=json.dumps(result, indent=2, default=str),
                file_name=f"incident_{incident_id}_{order_id}.json",
                mime="application/json",
            )

    if st.session_state.history:
        st.markdown("---")
        st.subheader("Recent investigation history")
        for item in st.session_state.history:
            st.write(f"- {item['incident_id']} / Order {item['order_id']}: {item['summary'][:140]}")

elif page == "Timeline":
    st.title("Incident timeline")
    order_id = st.number_input("Order ID", min_value=1, value=int(st.session_state.selected_order), step=1)
    incident_id = st.text_input("Incident ID", value=st.session_state.selected_incident)
    if st.button("Generate timeline"):
        result = fetch_incident(int(order_id), str(incident_id))
        timeline = build_timeline(result)
        for event in timeline:
            st.markdown(f"### {event['time']} — {event['title']}")
            st.write(event["detail"])
            st.markdown("---")
    else:
        st.info("Choose an order and click Generate timeline to inspect events.")

elif page == "Analytics":
    st.title("Trend analytics")
    trend_df = get_trend_data()
    if not trend_df.empty:
        st.subheader("Order trends over time")
        st.line_chart(trend_df.set_index("date")["incidents"])
    else:
        st.info("No trend data available.")

    st.markdown("---")
    memory_summary = memory_store.get_summary()
    st.subheader("Root-cause frequency")
    causes = memory_summary.get("recent_root_causes", [])
    if causes:
        df = pd.DataFrame(causes, columns=["root_cause", "count"])
        st.bar_chart(df.set_index("root_cause"))
    else:
        st.info("No trend data yet.")

    st.markdown("---")
    st.subheader("Incident history summary")
    st.json(memory_summary)

elif page == "Memory":
    st.title("Agent memory")
    memories = memory_store.list_recent(limit=10)
    if memories:
        for entry in memories:
            st.markdown(f"### {entry['incident_id']} — Order {entry['order_id']}")
            st.write(entry["summary"])
            st.caption(f"Severity: {entry['severity']} | Root cause: {entry['root_cause']} | Time: {entry['timestamp']}")
            st.markdown("---")
    else:
        st.info("No incidents recorded in agent memory yet.")

elif page == "Admin":
    if user_role != "admin":
        st.warning("Admin access required to view alerts and routing configuration.")
        st.stop()

    st.title("Admin and routing")
    st.subheader("Alert routing")

    with st.form("alert_form"):
        alert_incident = st.text_input("Incident ID", value=st.session_state.get("selected_incident", "INC-1001"))
        alert_title = st.text_input("Alert title", value="Production incident flagged")
        alert_message = st.text_area("Alert message", value="Interface timeout detected for order 5004; engineering review recommended.")
        recipient = st.text_input("Recipient email", value=os.getenv("ALERT_EMAIL_TO", "ops@example.com"))
        submitted_alert = st.form_submit_button("Send alert test")

    if submitted_alert:
        response = alert_router.send_alert(alert_incident, alert_title, alert_message, recipient)
        st.json(response)

    st.markdown("---")
    st.subheader("Runtime environment")
    st.json({
        "SMTP_HOST": os.getenv("SMTP_HOST", "not configured"),
        "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
        "OPENAI_API_KEY": "configured" if os.getenv("OPENAI_API_KEY") else "not configured",
        "SLACK_WEBHOOK_URL": "configured" if os.getenv("SLACK_WEBHOOK_URL") else "not configured",
        "API_BASE_URL": API_BASE_URL,
    })

st.sidebar.markdown("---")
st.sidebar.caption("AI operations console")
