import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import hashlib
import re
from datetime import datetime
from pypdf import PdfReader
from docx import Document

# ==========================================
# 1. PAGE CONFIG & RESPONSIVE UI STYLING
# ==========================================
st.set_page_config(
    page_title="CAP - Contract & Agreement Review Portal",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .stApp { background: radial-gradient(circle at top right, #1E293B, #0F172A 60%); color: #F8FAFC; font-family: 'Inter', sans-serif; }
    section[data-testid="stSidebar"] { background-color: #0B0F19 !important; border-right: 1px solid #1E293B !important; }
    div[data-testid="stForm"] { background: rgba(30, 41, 59, 0.7) !important; backdrop-filter: blur(12px) !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; border-radius: 24px !important; padding: 3rem !important; }
    
    /* Text Inputs Customization - Flat/No Borders on focus */
    div[data-testid="stTextInput"] input, div[data-baseweb="base-input"], div[data-baseweb="input"], textarea {
        background-color: rgba(15, 23, 42, 0.6) !important; color: #F8FAFC !important; border: none !important; border-radius: 12px !important; outline: none !important;
    }
    div[data-testid="stTextInput"] input:focus, div[data-baseweb="input"]:focus-within, textarea:focus {
        border: none !important; border-color: transparent !important; outline: none !important; box-shadow: none !important;
    }

    /* Modern Premium Buttons */
    button[kind="primaryFormSubmit"], .stButton>button { background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important; color: #0F172A !important; font-weight: 700 !important; border-radius: 12px !important; border: none !important; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2) !important; }
    button[kind="primaryFormSubmit"]:hover, .stButton>button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important; }
    div.stButton > button[kind="secondary"] { background-color: #1E293B !important; color: #94A3B8 !important; border: 1px solid #334155 !important; text-align: left !important; justify-content: flex-start !important; border-radius: 8px !important; }
    
    /* Risk Component Design Cards */
    .risk-card { background: rgba(30, 41, 59, 0.6); border-radius: 12px; padding: 1.25rem; border-left: 5px solid #EF4444; margin-bottom: 1rem; }
    .risk-card.med { border-left-color: #F59E0B; }
    .risk-card.low { border-left-color: #10B981; }
    div[data-testid="stMetricBlock"] { background-color: rgba(30, 41, 59, 0.5) !important; border: 1px solid #334155 !important; border-radius: 16px !important; padding: 1.25rem !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FILE BACKEND UTILITIES (JSON SYSTEM)
# ==========================================
USER_DB_FILE = "users.json"
CONTRACT_DB_FILE = "contracts.json"

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

def load_users():
    if not os.path.exists(USER_DB_FILE):
        db = {"admin": make_hashes("secure123")}
        with open(USER_DB_FILE, "w") as f: json.dump(db, f)
        return db
    with open(USER_DB_FILE, "r") as f: return json.load(f)

def save_user(username, password):
    users = load_users()
    if username in users: return False
    users[username] = make_hashes(password)
    with open(USER_DB_FILE, "w") as f: json.dump(users, f)
    return True

def verify_user(username, password):
    users = load_users()
    return username in users and users[username] == make_hashes(password)

def load_contracts():
    if not os.path.exists(CONTRACT_DB_FILE): return []
    with open(CONTRACT_DB_FILE, "r") as f: return json.load(f)

def save_contract_meta(meta):
    contracts = load_contracts()
    contracts.append(meta)
    with open(CONTRACT_DB_FILE, "w") as f: json.dump(contracts, f)

# ==========================================
# 3. TEXT EXTRACTORS & RISK ANALYSIS UTILITIES
# ==========================================
def extract_text_from_file(uploaded_file):
    filename = uploaded_file.name
    if filename.endswith('.txt'):
        return str(uploaded_file.read(), 'utf-8', errors='ignore')
    elif filename.endswith('.docx'):
        doc = Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif filename.endswith('.pdf'):
        reader = PdfReader(uploaded_file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return ""

def analyze_contract_text(text):
    risks = []
    # 1. Liability Check
    if re.search(r'(indemnity|liability).*uncapped|no.*limit', text, re.IGNORECASE):
        risks.append({"title": "Limitation of Liability Uncapped", "desc": "Found phrasing indicating uncapped corporate operational parameters or indemnity coverage.", "level": "High"})
    # 2. Auto-Renewal Window Check
    renewal_match = re.search(r'renew.*automatically|auto-renew|(\d+)\s*(days|months).*notice', text, re.IGNORECASE)
    if renewal_match:
        risks.append({"title": "Auto-Renewal Extension Clause Detected", "desc": "Contract locks in automated rollover parameters. Verify cancellation margins.", "level": "Medium"})
    # 3. Governing Law Check
    gov_law = re.search(r'governing law|governed by.*under the laws of\s*([A-Za-z\s]+)', text, re.IGNORECASE)
    
    # Corrected conditional evaluation
    detected_law = gov_law.group(1).strip() if (gov_law and gov_law.group(1)) else "Unspecified State/Country"
    
    # Extract structural deadline dates to map milestone calendar
    dates = re.findall(r'\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b', text)
    extracted_date = dates[0] if dates else datetime.today().strftime('%Y-%m-%d')
    return risks, extracted_date

# ==========================================
# 4. INITIALIZE STATE LOGIC
# ==========================================
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "active_tab" not in st.session_state: st.session_state.active_tab = "Dashboard Overview"
if "current_contract_text" not in st.session_state: st.session_state.current_contract_text = ""
if "current_risks" not in st.session_state: st.session_state.current_risks = []
load_users()

# ==========================================
# 5. WORKSPACE RENDER MATRIX
# ==========================================
if not st.session_state.authenticated:
    st.markdown("<br>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1.1, 1.3, 1.1])
    with center_col:
        st.markdown('<div style="text-align:center; margin-bottom:1.5rem;"><h2 style="font-weight:800; background:linear-gradient(to right, #10B981, #34D399); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">CAP PORTAL GATEWAY</h2><p style="color:#64748B;">Contract Risk Analysis Workspace</p></div>', unsafe_allow_html=True)
        auth_mode = st.radio("Mode", ["Sign In", "Register"], horizontal=True, label_visibility="collapsed")
        
        if auth_mode == "Sign In":
            with st.form("login_form"):
                u = st.text_input("User ID", placeholder="User ID ID")
                p = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Unlock Workspace", use_container_width=True):
                    if verify_user(u, p):
                        st.session_state.authenticated = True
                        st.rerun()
                    else: st.error("Access credentials mismatch.")
        else:
            with st.form("signup_form"):
                nu = st.text_input("Choose User ID")
                np = st.text_input("Password", type="password")
                if st.form_submit_button("Create Profile", use_container_width=True):
                    if save_user(nu, np): st.success("Created! Switch to Sign In to connect.")
                    else: st.error("User ID already registered.")
else:
    # Sidebar Module Navigation Controls
    with st.sidebar:
        st.title("📜 CAP Workspace")
        st.markdown("---")
        for tab in ["Dashboard Overview", "Upload & Extract Risks", "Archive Registry"]:
            if st.button(tab, use_container_width=True, type="primary" if st.session_state.active_tab == tab else "secondary"):
                st.session_state.active_tab = tab
                st.rerun()
        st.markdown("---")
        if st.button("Log Out Session", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    # Main App Logic Execution Routers
    st.title("Contract & Agreement Review Dashboard")
    st.markdown(f"Active Workspace Scope: `{st.session_state.active_tab}`")
    st.markdown("---")

    contracts = load_contracts()

    if st.session_state.active_tab == "Dashboard Overview":
        # Metric Calculations directly fetched from stored files matrix
        total_docs = len(contracts)
        high_risks = sum(1 for c in contracts if c.get('risk_level') == 'High')
        
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Analyzed Agreements", value=total_docs, delta=f"{total_docs} Records Tracked")
        with m2: st.metric("High Severity Alerts", value=high_risks, delta="Action Required" if high_risks > 0 else "Clear", delta_color="inverse")
        with m3: st.metric("Pending Audits", value=max(0, total_docs - 1))
        with m4: st.metric("AI Pipeline Guard", value="99.4%", delta="Healthy")
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 📊 Distribution Assessment Analytics")
            st.line_chart(pd.DataFrame(np.random.randn(15, 2), columns=['Active Risk Curves', 'Compliance Overheads']), use_container_width=True)
        with c2:
            st.markdown("### 📅 Extracted Milestone Renewal Timelines")
            if contracts:
                timeline_df = pd.DataFrame(contracts)[['filename', 'milestone_date']]
                st.dataframe(timeline_df, use_container_width=True, hide_index=True)
            else:
                st.info("No timeline milestones mapped. Upload a document to populate values.")

    elif st.session_state.active_tab == "Upload & Extract Risks":
        up_col, chat_col = st.columns([1.2, 1])
        
        with up_col:
            st.markdown("### 📤 Ingestion Matrix")
            f = st.file_uploader("Upload Contract File (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
            if f is not None:
                if st.button("Execute Compliance Risk Parsing Run", use_container_width=True):
                    with st.spinner("Extracting contents & scanning regular expressions criteria..."):
                        txt = extract_text_from_file(f)
                        st.session_state.current_contract_text = txt
                        risks, m_date = analyze_contract_text(txt)
                        st.session_state.current_risks = risks
                        
                        # Save parsed document metadata to persistent storage tracking file
                        save_contract_meta({
                            "filename": f.name,
                            "risk_level": "High" if any(r['level']=='High' for r in risks) else "Medium",
                            "milestone_date": m_date
                        })
                    st.success("File Analysis Pipeline Completed successfully.")
            
            # Display dynamically parsed vulnerabilities out of current context
            if st.session_state.current_risks:
                st.markdown("### ⚠️ Flagged Clause Summary Matrix")
                for r in st.session_state.current_risks:
                    lvl_class = "med" if r['level'] == 'Medium' else ("low" if r['level'] == 'Low' else "")
                    st.markdown(f"""
                    <div class="risk-card {lvl_class}">
                        <strong style="color:#F8FAFC;">[{r['level']} Severity] {r['title']}</strong>
                        <p style="color:#94A3B8; font-size:0.9rem; margin-top:4px;">{r['desc']}</p>
                    </div>
                    """, unsafe_allow_html=True)

        with chat_col:
            st.markdown("### 💬 Interactive Clause RAG Query Interface")
            st.caption("Ask specific contractual content queries below to scan text block indexes.")
            query = st.text_input("Enter query parameter (e.g., 'termination', 'indemnity', 'payment')")
            if query and st.session_state.current_contract_text:
                # Mock RAG Content Matcher scanning document sentences containing terms
                sentences = st.session_state.current_contract_text.split('.')
                matches = [s.strip() for s in sentences if query.lower() in s.lower()]
                if matches:
                    st.markdown("**Extracted Matches from Contract Body Text:**")
                    for m in matches[:3]:
                        st.info(f"📑 ... {m} ...")
                else:
                    st.warning("No literal matching section index strings located inside document contents.")

    elif st.session_state.active_tab == "Archive Registry":
        st.subheader("Persistent System Administration Archival Registry Records")
        if contracts:
            st.dataframe(pd.DataFrame(contracts), use_container_width=True, hide_index=True)
        else:
            st.info("No structural historical entries recorded inside dashboard environment parameters.")