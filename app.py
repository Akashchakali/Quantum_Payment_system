import base64
import hashlib
import io
import json
import random
import subprocess
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import qrcode
import streamlit as st


APP_PASSWORD = "quantum123"
QBER_THRESHOLD = 0.11
INITIAL_BALANCE = 75000.0
PROFILE_FILE = Path("user_profile.json")
PROJECT_VIDEO_FILE = Path("quantumpay_payment_flow.mp4")
PROJECT_VIDEO_WITH_MUSIC_FILE = Path("quantumpay_payment_flow_with_music.mp4")
PROJECT_MUSIC_FILE = Path("project_music.mp3")

DEFAULT_USER = {
    "name": "Akash Student",
    "bank": "Quantum National Bank",
    "account": "987654321012",
    "upi": "student@qpay",
    "upi_password": APP_PASSWORD,
}

CONTACTS = [
    {"name": "Sai Preethi", "number": "9123456780", "bank": "Quantum National Bank"},
    {"name": "Subhahan", "number": "9876501234", "bank": "Secure Trust Bank"},
    {"name": "sindhu", "number": "9988776655", "bank": "Future Finance Bank"},
    {"name": "Rishi", "number": "9090901234", "bank": "Digital India Bank"},
    {"name": "Ramesh Rao", "number": "9000011122", "bank": "Merchant Pay Bank"},
]

SELF_ACCOUNTS = [
    {"label": "Savings Account", "account": "987654321012", "balance_key": "main_balance"},
    {"label": "Wallet Account", "account": "876543210987", "balance_key": "wallet_balance"},
    {"label": "Scholarship Account", "account": "765432109876", "balance_key": "scholarship_balance"},
]


st.set_page_config(
    page_title="QuantumPay Shield",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --panel: rgba(8, 28, 25, 0.82);
            --line: rgba(103, 232, 205, 0.24);
            --text: #e8fff9;
            --muted: #a7c9c0;
            --mint: #5eead4;
            --green: #34d399;
            --red: #fb7185;
            --yellow: #facc15;
        }
        .stApp {
            color: var(--text);
            background:
                radial-gradient(circle at 12% 18%, rgba(94, 234, 212, 0.18), transparent 24%),
                radial-gradient(circle at 82% 8%, rgba(250, 204, 21, 0.12), transparent 22%),
                linear-gradient(125deg, #06110f 0%, #10231f 45%, #081614 100%);
        }
        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            z-index: -2;
            background-image:
                linear-gradient(rgba(94, 234, 212, 0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(94, 234, 212, 0.08) 1px, transparent 1px);
            background-size: 44px 44px;
        }
        .stApp::after {
            content: "";
            position: fixed;
            inset: -30%;
            z-index: -1;
            background:
                radial-gradient(circle, rgba(94, 234, 212, 0.22) 0 2px, transparent 3px),
                radial-gradient(circle, rgba(250, 204, 21, 0.18) 0 1px, transparent 3px);
            background-size: 90px 90px, 130px 130px;
            animation: drift 24s linear infinite;
            opacity: 0.45;
        }
        @keyframes drift {
            from { transform: translate3d(0, 0, 0) rotate(0deg); }
            to { transform: translate3d(70px, -90px, 0) rotate(4deg); }
        }
        .block-container { padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1180px; }
        header[data-testid="stHeader"] { background: transparent; }
        div[data-testid="stToolbar"] { display: none; }
        h1, h2, h3, p, label, span, div { letter-spacing: 0; }
        h1, h2, h3 { color: var(--text); }
        label, label p, div[data-testid="stWidgetLabel"], div[data-testid="stWidgetLabel"] p,
        div[data-testid="stRadio"] label, div[data-testid="stRadio"] p,
        div[data-baseweb="radio"] label, div[data-baseweb="radio"] div,
        div[data-testid="stSelectbox"] label, div[data-testid="stTextInput"] label,
        div[data-testid="stNumberInput"] label {
            color: #d8fff7 !important;
        }
        div[data-baseweb="select"] span, div[data-baseweb="select"] div,
        div[data-testid="stMarkdownContainer"] p {
            color: #d8fff7;
        }
        input::placeholder {
            color: #9fbdb5 !important;
            opacity: 1 !important;
        }
        .topbar, .metric-card, .soft-card, .action-card {
            border: 1px solid var(--line);
            background: var(--panel);
            border-radius: 8px;
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.22);
            backdrop-filter: blur(16px);
        }
        .topbar {
            display: flex; justify-content: space-between; align-items: center;
            gap: 18px; padding: 18px 20px; margin-bottom: 18px;
        }
        .brand { display: flex; align-items: center; gap: 12px; }
        .brand-mark {
            width: 44px; height: 44px; border-radius: 8px;
            background: conic-gradient(from 210deg, #5eead4, #facc15, #34d399, #5eead4);
            color: #04100e; display: grid; place-items: center; font-weight: 900; font-size: 22px;
            box-shadow: 0 0 24px rgba(94, 234, 212, 0.36);
        }
        .brand h1 { margin: 0; font-size: 26px; line-height: 1.1; }
        .brand p, .hint, .action-card p, .metric-card p { color: var(--muted); }
        .brand p { margin: 3px 0 0; font-size: 14px; }
        .status-pill {
            border: 1px solid rgba(94, 234, 212, 0.42); color: #ccfff6;
            background: rgba(94, 234, 212, 0.08); padding: 9px 12px; border-radius: 8px; font-size: 14px;
        }
        .metric-row, .action-grid { display: grid; gap: 14px; margin: 14px 0 22px; }
        .metric-row { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        .action-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .metric-card { padding: 16px; min-height: 112px; }
        .metric-card p { margin: 0 0 10px; font-size: 13px; }
        .metric-card h3 { margin: 0; font-size: 26px; }
        .metric-card small { color: #bff7ed; }
        .soft-card { padding: 18px; margin-bottom: 16px; }
        .action-card { padding: 18px; min-height: 155px; position: relative; overflow: hidden; }
        .action-card h3 { margin: 0 0 8px; font-size: 20px; }
        .action-card p, .hint { margin: 0; font-size: 14px; line-height: 1.55; }
        .stButton > button, .stDownloadButton > button, button[kind="primary"], button[kind="secondary"], button[data-testid="baseButton-secondary"], button[data-testid="baseButton-primary"] {
            width: 100%; border-radius: 8px; border: 1px solid rgba(94, 234, 212, 0.42);
            background: linear-gradient(135deg, #37cfc0, #f0bd05) !important; color: #03110f !important;
            font-weight: 900; min-height: 45px; text-shadow: none;
        }
        .stButton > button:hover, .stDownloadButton > button:hover, button[kind="primary"]:hover, button[kind="secondary"]:hover {
            transform: translateY(-1px); box-shadow: 0 10px 26px rgba(94, 234, 212, 0.24); color: #03110f !important;
            border-color: rgba(255, 255, 255, 0.74);
        }
        .stButton > button p, .stDownloadButton > button p,
        .stButton > button span, .stDownloadButton > button span,
        button p, button span {
            color: #03110f !important;
            font-weight: 900 !important;
        }
        button:disabled, button[disabled] {
            opacity: 1 !important;
            background: linear-gradient(135deg, #5eead4, #facc15) !important;
            color: #03110f !important;
        }
        div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-baseweb="select"] > div, textarea {
            border-radius: 8px !important; border-color: rgba(94, 234, 212, 0.28) !important;
            background: rgba(6, 17, 15, 0.76) !important; color: var(--text) !important;
        }
        .success-animation, .failure-animation {
            display: flex; align-items: center; gap: 16px; padding: 18px; border-radius: 8px;
            margin: 16px 0; border: 1px solid var(--line); animation: popin 0.36s ease both;
        }
        .success-animation { background: rgba(52, 211, 153, 0.12); }
        .failure-animation { background: rgba(251, 113, 133, 0.12); }
        .checkmark, .crossmark {
            width: 54px; height: 54px; border-radius: 50%; display: grid; place-items: center;
            flex: 0 0 54px; font-size: 30px; font-weight: 900;
        }
        .checkmark { background: #34d399; color: #042017; animation: pulse-ok 1.1s ease-in-out infinite; }
        .crossmark { background: #fb7185; color: #2a050b; animation: shake 0.6s ease both; }
        .coin-stage {
            display: grid;
            place-items: center;
            min-height: 120px;
            margin: 12px 0;
        }
        .coin {
            width: 84px;
            height: 84px;
            border-radius: 50%;
            display: grid;
            place-items: center;
            color: #04100e;
            font-size: 28px;
            font-weight: 900;
            background: radial-gradient(circle at 30% 25%, #fff7ad, #facc15 42%, #b7791f 100%);
            border: 3px solid rgba(255, 255, 255, 0.46);
            box-shadow: 0 0 36px rgba(250, 204, 21, 0.46);
            animation: coin-flip 1.25s ease-out both;
        }
        .success-animation h3, .failure-animation h3 { margin: 0 0 4px; }
        .success-animation p, .failure-animation p { margin: 0; color: var(--muted); }
        .quantum-strip {
            height: 8px; overflow: hidden; background: rgba(94, 234, 212, 0.1);
            border-radius: 8px; margin: 12px 0; position: relative;
        }
        .quantum-strip::before {
            content: ""; position: absolute; inset: 0; width: 45%;
            background: linear-gradient(90deg, transparent, #5eead4, #facc15, transparent);
            animation: scan 1.5s linear infinite;
        }
        .secure { color: #86efac; font-weight: 800; }
        .danger { color: #fda4af; font-weight: 800; }
        div[data-testid="stExpander"] details {
            background: rgba(8, 28, 25, 0.82) !important;
            border: 1px solid rgba(94, 234, 212, 0.24) !important;
            border-radius: 8px !important;
        }
        div[data-testid="stExpander"] summary, div[data-testid="stExpander"] summary p {
            color: #e8fff9 !important;
            font-weight: 800 !important;
        }
        @keyframes pulse-ok {
            0%, 100% { transform: scale(1); box-shadow: 0 0 0 rgba(52, 211, 153, 0.32); }
            50% { transform: scale(1.08); box-shadow: 0 0 28px rgba(52, 211, 153, 0.42); }
        }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-4px); }
            50% { transform: translateX(4px); }
            75% { transform: translateX(-2px); }
        }
        @keyframes popin {
            from { transform: scale(0.98); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        @keyframes scan {
            from { transform: translateX(-100%); }
            to { transform: translateX(260%); }
        }
        @keyframes coin-flip {
            0% { transform: translateY(28px) rotateY(0deg) scale(0.72); opacity: 0; }
            35% { transform: translateY(-18px) rotateY(540deg) scale(1.06); opacity: 1; }
            72% { transform: translateY(4px) rotateY(900deg) scale(1); }
            100% { transform: translateY(0) rotateY(1080deg) scale(1); }
        }
        @media (max-width: 900px) {
            .metric-row, .action-grid { grid-template-columns: 1fr 1fr; }
            .topbar { align-items: flex-start; flex-direction: column; }
        }
        @media (max-width: 620px) {
            .metric-row, .action-grid { grid-template-columns: 1fr; }
            .brand h1 { font-size: 22px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state():
    # ---------- SESSION STATE ----------
    saved_profile = load_saved_profile()
    defaults = {
        "main_balance": INITIAL_BALANCE,
        "wallet_balance": 12000.0,
        "scholarship_balance": 28000.0,
        "transactions": [],
        "payment_attempts": 0,
        "last_quantum": None,
        "last_result": None,
        "pending_payment": None,
        "active_page": "Home",
        "page_history": [],
        "demo_mode": True,
        "logged_in": False,
        "user_profile": saved_profile,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_saved_profile():
    # ---------- USER PROFILE ----------
    if not PROFILE_FILE.exists():
        return DEFAULT_USER.copy()
    try:
        profile = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_USER.copy()

    required = {"name", "bank", "account", "upi", "upi_password"}
    if not required.issubset(profile):
        return DEFAULT_USER.copy()
    return profile


def save_profile(profile):
    PROFILE_FILE.write_text(json.dumps(profile, indent=2), encoding="utf-8")


def money(value):
    return f"INR {value:,.2f}"


def short_key(bits, size=32):
    joined = "".join(str(bit) for bit in bits)
    return joined[:size] + ("..." if len(joined) > size else "")


def verify_password(password):
    # ---------- PASSWORD CHECK ----------
    profile = st.session_state.get("user_profile", DEFAULT_USER)
    return password == profile.get("upi_password", APP_PASSWORD)


def make_txn_id():
    return f"QTX{datetime.now().strftime('%H%M%S')}{random.randint(100, 999)}"


def is_valid_10_digit_number(value):
    return bool(value) and value.isdigit() and len(value) == 10


def is_valid_12_digit_account(value):
    return bool(value) and value.isdigit() and len(value) == 12


def lookup_name_for_number(number):
    saved = {contact["number"]: contact["name"] for contact in CONTACTS}
    if number in saved:
        return saved[number]

    first_names = ["Arjun", "Kavya", "Nikhil", "Priya", "Vikram", "Ananya", "Rahul", "Diya"]
    last_names = ["Patel", "Nair", "Reddy", "Singh", "Das", "Kumar", "Menon", "Joshi"]
    seed = int(number[-4:])
    return f"{first_names[seed % len(first_names)]} {last_names[(seed // 7) % len(last_names)]}"


def lookup_name_for_account(account):
    saved_accounts = {item["account"]: item["label"] for item in SELF_ACCOUNTS}
    if account in saved_accounts:
        return saved_accounts[account]

    first_names = ["Aditya", "Ishaan", "Neha", "Sanjay", "Pooja", "Kiran", "Manav", "Divya"]
    last_names = ["Shah", "Kapoor", "Rao", "Bose", "Mehta", "Pillai", "Agarwal", "Shetty"]
    seed = int(account[-5:])
    return f"{first_names[seed % len(first_names)]} {last_names[(seed // 11) % len(last_names)]}"


def bb84_simulation(num_qubits=96, forced_mode="secure"):
    # ---------- BB84 SIMULATION ----------
    alice_bits = np.random.randint(0, 2, num_qubits).tolist()
    alice_bases = np.random.choice(["+", "x"], num_qubits).tolist()
    bob_bases = np.random.choice(["+", "x"], num_qubits).tolist()
    eve_present = forced_mode == "attack"
    bob_bits = []

    for bit, alice_basis, bob_basis in zip(alice_bits, alice_bases, bob_bases):
        transmitted_bit = bit
        if eve_present and random.choice(["+", "x"]) != alice_basis:
            transmitted_bit = random.randint(0, 1)
        bob_bits.append(transmitted_bit if bob_basis == alice_basis else random.randint(0, 1))

    matched_positions = [idx for idx, pair in enumerate(zip(alice_bases, bob_bases)) if pair[0] == pair[1]]
    alice_key = [alice_bits[idx] for idx in matched_positions]
    bob_key = [bob_bits[idx] for idx in matched_positions]
    sample_size = max(8, int(len(matched_positions) * 0.28))
    sample_positions = list(range(min(sample_size, len(matched_positions))))
    mismatches = sum(1 for idx in sample_positions if alice_key[idx] != bob_key[idx])
    qber = (mismatches / len(sample_positions) * 100) if sample_positions else 0.0

    if forced_mode == "secure":
        qber = round(random.uniform(0.03, 0.10), 2)
        secure = True
    elif forced_mode == "attack":
        qber = round(random.uniform(0.12, 0.30), 2)
        secure = False
    else:
        qber = round(qber, 2)
        secure = qber <= QBER_THRESHOLD
        if secure and qber == 0.0:
            qber = round(random.uniform(0.03, 0.10), 2)

    shared_key = alice_key[sample_size:] if len(alice_key) > sample_size else alice_key
    if len(shared_key) < 16:
        shared_key = alice_bits[:32]

    return {
        "alice_bits": alice_bits,
        "alice_bases": alice_bases,
        "bob_bases": bob_bases,
        "bob_bits": bob_bits,
        "matched_positions": matched_positions,
        "shared_key": shared_key,
        "key_length": len(shared_key),
        "qber": qber,
        "secure": secure,
        "eve_present": eve_present,
        "threshold": QBER_THRESHOLD,
    }


def demo_outcome_for_attempt(attempt):
    cycle_position = ((attempt - 1) % 2) + 1
    if cycle_position == 1:
        return "success_secure"
    if cycle_position == 2:
        return "fail_attack"
    return "dynamic"


def scenario_label(outcome):
    labels = {
        "success_secure": "Secure BB84 channel: payment approved",
        "fail_attack": "Eavesdropping demo: high QBER blocks payment",
        "fail_balance": "Secure channel but insufficient balance demo",
        "dynamic": "Dynamic BB84 simulation",
    }
    return labels.get(outcome, "Dynamic BB84 simulation")


def encrypt_payload(payload, shared_key):
    # ---------- PAYLOAD ENCRYPTION ----------
    key_material = "".join(str(bit) for bit in shared_key) or "0"
    key_hash = hashlib.sha256(key_material.encode()).digest()
    plain = payload.encode()
    cipher = bytes([char ^ key_hash[idx % len(key_hash)] for idx, char in enumerate(plain)])
    return base64.urlsafe_b64encode(cipher).decode()


def add_transaction(txn):
    st.session_state.transactions.insert(0, txn)


def show_topbar():
    success = sum(1 for txn in st.session_state.transactions if txn["status"] == "Success")
    failed = sum(1 for txn in st.session_state.transactions if txn["status"] == "Failed")
    profile = st.session_state.get("user_profile", DEFAULT_USER)
    user_text = f"{profile['name']} | {profile['bank']}" if st.session_state.get("logged_in") else "Login required"
    st.markdown(
        f"""
        <div class="topbar">
            <div class="brand">
                <div class="brand-mark">Q</div>
                <div>
                    <h1>QuantumPay Shield</h1>
                    <p>BB84 secured payment simulator with QBER based authorization</p>
                </div>
            </div>
            <div class="status-pill">{user_text} | Success: {success} | Failed: {failed}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_metrics():
    total = st.session_state.main_balance + st.session_state.wallet_balance + st.session_state.scholarship_balance
    txns = st.session_state.transactions
    latest_qber = txns[0]["qber"] if txns else 0.0
    secure_txns = sum(1 for txn in txns if txn["status"] == "Success")
    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-card"><p>Total Available Balance</p><h3>{money(total)}</h3><small>Main, wallet, and scholarship accounts</small></div>
            <div class="metric-card"><p>Main Account</p><h3>{money(st.session_state.main_balance)}</h3><small>Primary payment account</small></div>
            <div class="metric-card"><p>Latest QBER</p><h3>{latest_qber:.2f}%</h3><small>Threshold is {QBER_THRESHOLD:.2f}%</small></div>
            <div class="metric-card"><p>Secure Transactions</p><h3>{secure_txns}</h3><small>Approved after BB84 verification</small></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_dashboard_overview():
    txns = st.session_state.transactions
    latest = txns[0] if txns else None
    latest_qber = latest["qber"] if latest else None
    key_length = latest["key_length"] if latest else 0
    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-card"><p>Payment Attempts</p><h3>{len(txns)}</h3><small>Demo flow tracks success and failure</small></div>
            <div class="metric-card"><p>Latest QBER</p><h3>{latest_qber:.2f}%</h3><small>Last transaction security reading</small></div>
            <div class="metric-card"><p>Generated Key Length</p><h3>{key_length}</h3><small>Bits from the latest BB84 run</small></div>
            <div class="metric-card"><p>QBER Limit</p><h3>{QBER_THRESHOLD:.2f}%</h3><small>Above this, payment is blocked</small></div>
        </div>
        """ if latest else
        f"""
        <div class="metric-row">
            <div class="metric-card"><p>Payment Attempts</p><h3>0</h3><small>Start with Make Payment</small></div>
            <div class="metric-card"><p>Latest QBER</p><h3>Not run</h3><small>Shown after BB84 verification</small></div>
            <div class="metric-card"><p>Generated Key</p><h3>Waiting</h3><small>Created during payment</small></div>
            <div class="metric-card"><p>QBER Limit</p><h3>{QBER_THRESHOLD:.2f}%</h3><small>Above this, payment is blocked</small></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_button(label, page):
    if st.button(label, use_container_width=True):
        navigate_to(page)
        st.rerun()


def navigate_to(page, remember=True):
    current = st.session_state.get("active_page", "Home")
    if remember and page != current:
        st.session_state.page_history.append(current)
    st.session_state.active_page = page


def go_back():
    history = st.session_state.get("page_history", [])
    if history:
        st.session_state.active_page = history.pop()
    else:
        st.session_state.active_page = "Home"
    st.rerun()


def navigation_buttons(primary_label="Go to Home", primary_page="Home", secondary_label=None, secondary_page=None):
    if secondary_label:
        cols = st.columns([0.8, 1.2, 1.2, 3.8])
    else:
        cols = st.columns([0.8, 1.2, 4])
    with cols[0]:
        if st.button("<", use_container_width=True):
            go_back()
    with cols[1]:
        page_button(primary_label, primary_page)
    if secondary_label and secondary_page:
        with cols[2]:
            page_button(secondary_label, secondary_page)


def logout():
    st.session_state.logged_in = False
    navigate_to("Home", remember=False)
    st.session_state.page_history = []
    st.session_state.last_result = None
    st.session_state.last_quantum = None
    st.rerun()


def queue_payment(payment):
    st.session_state.pending_payment = payment
    navigate_to("Confirm Payment")
    st.rerun()


def password_gate(label, key):
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.subheader(label)
    password = st.text_input("Enter password", type="password", key=key)
    st.caption("Use your UPI password. Demo existing-user password is quantum123.")
    st.markdown("</div>", unsafe_allow_html=True)
    return password


def contact_selector():
    options = [c["name"] for c in CONTACTS]
    selected = st.selectbox("Select contact", options)
    contact = CONTACTS[options.index(selected)]
    st.info(f"Saved number: {contact['number']} | Bank: {contact['bank']}")
    return contact


def show_processing_animation():
    # ---------- QUANTUM PROCESSING ANIMATION ----------
    placeholder = st.empty()
    steps = [
        "Generating random quantum bits",
        "Selecting Alice and Bob measurement bases",
        "Sifting matching bases",
        "Calculating QBER",
        "Encrypting payment payload",
        "Authorizing transaction",
    ]
    for step in steps:
        placeholder.markdown(
            f"""
            <div class="soft-card">
                <h3>{step}</h3>
                <div class="quantum-strip"></div>
                <p class="hint">Quantum channel verification is running...</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        time.sleep(0.25)
    placeholder.empty()


def render_result(result):
    if result["status"] == "Success":
        st.markdown(
            f"""
            <div class="coin-stage"><div class="coin">INR</div></div>
            <div class="success-animation">
                <div class="checkmark">OK</div>
                <div>
                    <h3>Payment successful</h3>
                    <p>{result['message']}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="failure-animation">
                <div class="crossmark">X</div>
                <div>
                    <h3>Payment failed</h3>
                    <p>{result['message']}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_quantum_summary(quantum, encrypted_payload):
    status_class = "secure" if quantum["secure"] else "danger"
    status_text = "Secure channel" if quantum["secure"] else "Eavesdropping detected"
    st.markdown(
        f"""
        <div class="soft-card">
            <h3>Quantum Security Report</h3>
            <p>Status: <span class="{status_class}">{status_text}</span></p>
            <p>QBER: <b>{quantum['qber']:.2f}%</b> | Threshold: <b>{quantum['threshold']:.2f}%</b> | Shared key length: <b>{quantum['key_length']} bits</b></p>
            <p class="hint">Shared key preview: {short_key(quantum['shared_key'])}</p>
            <p class="hint">Encrypted payment payload: {encrypted_payload[:96]}...</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("View BB84 sample data"):
        render_bb84_sample_table(quantum)


def basis_arrow(basis):
    return "&uarr;" if basis == "+" else "&nearr;"


def render_bb84_sample_table(quantum):
    rows = []
    for idx in range(min(24, len(quantum["alice_bits"]))):
        alice_basis = quantum["alice_bases"][idx]
        bob_basis = quantum["bob_bases"][idx]
        matched = alice_basis == bob_basis
        rows.append(
            "<tr>"
            f"<td>{idx + 1}</td>"
            f"<td>{quantum['alice_bits'][idx]}</td>"
            f"<td>{basis_arrow(alice_basis)} <span>{alice_basis}</span></td>"
            f"<td>{basis_arrow(bob_basis)} <span>{bob_basis}</span></td>"
            f"<td>{quantum['bob_bits'][idx]}</td>"
            f"<td class=\"{'match' if matched else 'mismatch'}\">{'&#10003; Matched' if matched else '&#10007; Mismatched'}</td>"
            "</tr>"
        )

    html = f"""
        <style>
        .bb84-table {{
            width: 100%;
            border-collapse: collapse;
            overflow: hidden;
            border-radius: 8px;
            border: 1px solid rgba(94, 234, 212, 0.28);
            background: rgba(5, 19, 16, 0.95);
            color: #e8fff9;
        }}
        .bb84-table th {{
            background: rgba(94, 234, 212, 0.16);
            color: #e8fff9;
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid rgba(94, 234, 212, 0.22);
        }}
        .bb84-table td {{
            padding: 9px 10px;
            color: #d8fff7;
            border-bottom: 1px solid rgba(94, 234, 212, 0.11);
        }}
        .bb84-table tr:nth-child(even) td {{
            background: rgba(255, 255, 255, 0.025);
        }}
        .bb84-table .match {{
            color: #86efac;
            font-weight: 900;
        }}
        .bb84-table .mismatch {{
            color: #fda4af;
            font-weight: 900;
        }}
        </style>
        <table class="bb84-table">
            <thead>
                <tr>
                    <th>No.</th>
                    <th>Alice Bit</th>
                    <th>Alice Basis</th>
                    <th>Bob Basis</th>
                    <th>Bob Bit</th>
                    <th>Basis Result</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
    st.html(html)


def process_payment(payment_type, receiver_name, receiver_account, amount, note, password, source_key="main_balance", destination_key=None):
    # ---------- PAYMENT ----------
    if not verify_password(password):
        result = {"status": "Failed", "message": "Incorrect password. Access denied before BB84 verification."}
        st.session_state.last_result = result
        render_result(result)
        return

    if amount <= 0:
        result = {"status": "Failed", "message": "Enter a valid payment amount."}
        st.session_state.last_result = result
        render_result(result)
        return

    st.session_state.payment_attempts += 1
    attempt = st.session_state.payment_attempts
    outcome = demo_outcome_for_attempt(attempt) if st.session_state.demo_mode else "dynamic"
    forced_mode = "attack" if outcome == "fail_attack" else ("secure" if outcome in ["success_secure", "fail_balance"] else "dynamic")
    quantum = bb84_simulation(forced_mode=forced_mode)
    scenario = scenario_label(outcome)

    show_processing_animation()

    source_balance = st.session_state[source_key]
    force_insufficient = outcome == "fail_balance"
    secure_channel = quantum["secure"]
    enough_balance = source_balance >= amount and not force_insufficient
    payload = f"{payment_type}|{receiver_name}|{receiver_account}|{amount}|{note}|{datetime.now().isoformat()}"
    encrypted_payload = encrypt_payload(payload, quantum["shared_key"])

    if not secure_channel:
        status = "Failed"
        reason = "Eavesdropping detected. QBER crossed the allowed threshold."
        message = f"QBER is {quantum['qber']:.2f}%, so the payment was blocked."
    elif not enough_balance:
        status = "Failed"
        reason = "Insufficient balance."
        message = "The quantum channel is secure, but the source account does not have enough balance for this demo payment."
    else:
        status = "Success"
        reason = "Secure quantum channel verified."
        message = f"{money(amount)} sent to {receiver_name}. The payload was encrypted with the BB84 shared key."
        st.session_state[source_key] -= amount
        if destination_key:
            st.session_state[destination_key] += amount

    txn = {
        "id": make_txn_id(),
        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "type": payment_type,
        "receiver": receiver_name,
        "account": receiver_account,
        "amount": float(amount),
        "status": status,
        "qber": float(quantum["qber"]),
        "key_length": int(quantum["key_length"]),
        "shared_key_preview": short_key(quantum["shared_key"]),
        "scenario": scenario,
        "reason": reason,
        "encrypted_payload": encrypted_payload[:70] + "...",
        "balance_after": float(st.session_state.main_balance),
    }
    add_transaction(txn)
    st.session_state.last_quantum = quantum
    result = {
        "status": status,
        "message": message,
        "transaction": txn,
        "quantum": quantum,
        "encrypted_payload": encrypted_payload,
        "scenario": scenario,
    }
    st.session_state.last_result = result
    navigate_to("Payment Receipt")
    st.rerun()


def show_home():
    # ---------- HOME PAGE ----------
    show_dashboard_overview()
    st.markdown(
        """
        <div class="soft-card">
            <h2>Choose an action</h2>
            <p class="hint">Every sensitive banking action is protected by password verification. Payments also pass through BB84 key generation and QBER analysis before authorization.</p>
        </div>
        <div class="action-grid">
            <div class="action-card"><h3>Make Payment</h3><p>Pay a saved contact or enter a custom account. The quantum channel is checked before money moves.</p></div>
            <div class="action-card"><h3>Transfer Money</h3><p>Transfer to your own account or to another 12-digit bank account after quantum verification.</p></div>
            <div class="action-card"><h3>Balance Enquiry</h3><p>View account balances after password verification.</p></div>
            <div class="action-card"><h3>Transaction History</h3><p>Review successful and failed attempts with QBER values and failure reasons.</p></div>
            <div class="action-card"><h3>Graph Analysis</h3><p>Analyze QBER trend, payment status, balance movement, and attack detection.</p></div>
            <div class="action-card"><h3>Generate QR Code</h3><p>Create a simple QR code for your payment identity.</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    with cols[0]:
        page_button("Make Payment", "Make Payment")
        page_button("Transfer Money", "Transfer Money")
    with cols[1]:
        page_button("Balance Enquiry", "Balance Enquiry")
        page_button("Transaction History", "Transaction History")
    with cols[2]:
        page_button("Graph Analysis", "Graph Analysis")
        page_button("Generate QR Code", "Generate QR Code")

    st.markdown(
        """
        <div class="soft-card">
            <h3>Project Video</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    project_cols = st.columns([1.4, 4])
    with project_cols[0]:
        page_button("Open Project Video", "Project Video")


def login_page():
    # ---------- LOGIN PAGE ----------
    show_topbar()
    st.markdown(
        """
        <div class="soft-card">
            <h2>Login to QuantumPay</h2>
            <p class="hint">Choose an existing demo account to auto-fill details, or create a new user profile before opening the payment dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_type = st.radio("Are you an existing user?", ["Yes, existing user", "No, new user"], horizontal=True)

    if user_type == "Yes, existing user":
        saved_profile = st.session_state.get("user_profile", DEFAULT_USER)
        with st.form("existing_login"):
            name = st.text_input("Name", value=saved_profile["name"])
            bank = st.text_input("Bank", value=saved_profile["bank"])
            account = st.text_input("12-digit account number", value=saved_profile["account"], max_chars=12)
            upi = st.text_input("UPI ID", value=saved_profile["upi"])
            password = st.text_input("Enter UPI password", type="password")
            submitted = st.form_submit_button("Enter")
            if submitted:
                if not is_valid_12_digit_account(account):
                    render_result({"status": "Failed", "message": "Account number must contain exactly 12 digits."})
                    return
                if password == saved_profile["upi_password"]:
                    profile = {
                        "name": name,
                        "bank": bank,
                        "account": account,
                        "upi": upi,
                        "upi_password": saved_profile["upi_password"],
                    }
                    save_profile(profile)
                    st.session_state.user_profile = profile
                    st.session_state.logged_in = True
                    navigate_to("Home", remember=False)
                    st.rerun()
                else:
                    render_result({"status": "Failed", "message": "Incorrect UPI password. Login blocked."})
    else:
        banks = ["Quantum National Bank", "Secure Trust Bank", "Future Finance Bank", "Digital India Bank"]
        with st.form("new_login"):
            name = st.text_input("Full name", value="")
            bank = st.selectbox("Select your bank", banks)
            account = st.text_input("12-digit bank account number", value="", max_chars=12)
            upi = st.text_input("Create / enter UPI ID", value="")
            password = st.text_input("Create UPI password", type="password")
            submitted = st.form_submit_button("Create Account and Enter")
            if submitted:
                if not name or not account or not upi or not password:
                    render_result({"status": "Failed", "message": "Please fill all login details."})
                elif not is_valid_12_digit_account(account):
                    render_result({"status": "Failed", "message": "Account number must contain exactly 12 digits."})
                else:
                    profile = {
                        "name": name,
                        "bank": bank,
                        "account": account,
                        "upi": upi,
                        "upi_password": password,
                    }
                    save_profile(profile)
                    st.session_state.user_profile = profile
                    st.session_state.logged_in = True
                    navigate_to("Home", remember=False)
                    st.rerun()


def make_payment_page():
    # ---------- MAKE PAYMENT PAGE ----------
    st.header("Make Payment")
    st.markdown(
        '<p class="hint">Enter payment details first. After clicking Pay, the app asks for your UPI password and then runs BB84/QBER verification. Demo mode alternates one success and one attack failure.</p>',
        unsafe_allow_html=True,
    )
    st.toggle("Demo mode: one success, then one QBER failure", key="demo_mode")
    pay_mode = st.radio("Receiver type", ["Saved contact", "Custom account"], horizontal=True)

    if pay_mode == "Saved contact":
        contact = contact_selector()
        receiver_name = contact["name"]
        receiver_account = contact["number"]
    else:
        receiver_account = st.text_input("Enter 10-digit receiver number", value="", max_chars=10)
        if is_valid_10_digit_number(receiver_account):
            receiver_name = lookup_name_for_number(receiver_account)
            st.success(f"Receiver found: {receiver_name}")
        else:
            receiver_name = ""
            if receiver_account:
                st.warning("Enter exactly 10 digits to find the receiver.")

    cols = st.columns(2)
    with cols[0]:
        amount = st.number_input("Amount", min_value=1.0, value=1500.0, step=100.0)
    with cols[1]:
        note = st.text_input("Payment note", value="Quantum secured transfer")

    pay_cols = st.columns([2, 4])
    with pay_cols[0]:
        if st.button("Pay", type="primary", use_container_width=True):
            if pay_mode == "Custom account" and not is_valid_10_digit_number(receiver_account):
                render_result({"status": "Failed", "message": "Enter a valid 10-digit receiver number before payment."})
                return
            queue_payment(
                {
                    "payment_type": "Contact Payment",
                    "receiver_name": receiver_name,
                    "receiver_account": receiver_account,
                    "amount": amount,
                    "note": note,
                    "source_key": "main_balance",
                    "destination_key": None,
                }
            )
    navigation_buttons()


def transfer_money_page():
    st.header("Transfer Money")
    st.markdown(
        '<p class="hint">Choose a self transfer or send to another 12-digit bank account. The receiver name appears after a valid account number is entered.</p>',
        unsafe_allow_html=True,
    )
    account_labels = [f"{a['label']} | {a['account']}" for a in SELF_ACCOUNTS]
    source_label = st.selectbox("From account", account_labels, index=0)
    source = SELF_ACCOUNTS[account_labels.index(source_label)]

    transfer_type = st.radio("Transfer type", ["Self account", "Another bank account"], horizontal=True)
    destination_key = None

    if transfer_type == "Self account":
        destination_label = st.selectbox("To account", account_labels, index=1)
        destination = SELF_ACCOUNTS[account_labels.index(destination_label)]
        receiver_name = destination["label"]
        receiver_account = destination["account"]
        destination_key = destination["balance_key"]

        if source["balance_key"] == destination["balance_key"]:
            st.warning("Choose two different accounts.")
            navigation_buttons()
            return
    else:
        receiver_account = st.text_input("Enter 12-digit receiver account number", value="", max_chars=12)
        destination_key = None
        if is_valid_12_digit_account(receiver_account):
            receiver_name = lookup_name_for_account(receiver_account)
            st.success(f"Account holder found: {receiver_name}")
        else:
            receiver_name = ""
            if receiver_account:
                st.warning("Enter exactly 12 digits to find the account holder.")

    amount = st.number_input("Transfer amount", min_value=1.0, value=1000.0, step=100.0)
    note = st.text_input("Transfer note", value="Quantum secured bank transfer")

    pay_cols = st.columns([2, 4])
    with pay_cols[0]:
        if st.button("Pay", type="primary", use_container_width=True):
            if transfer_type == "Another bank account" and not is_valid_12_digit_account(receiver_account):
                render_result({"status": "Failed", "message": "Enter a valid 12-digit receiver account number before payment."})
                return
            queue_payment(
                {
                    "payment_type": "Self Transfer" if transfer_type == "Self account" else "Bank Account Transfer",
                    "receiver_name": receiver_name,
                    "receiver_account": receiver_account,
                    "amount": amount,
                    "note": note,
                    "source_key": source["balance_key"],
                    "destination_key": destination_key,
                }
            )
    navigation_buttons()


def balance_page():
    st.header("Balance Enquiry")
    password = password_gate("Balance Access", "balance_password")
    if st.button("Show Balance", type="primary"):
        if verify_password(password):
            st.markdown(
                """
                <div class="success-animation">
                    <div class="checkmark">OK</div>
                    <div>
                        <h3>Access granted</h3>
                        <p>Your accounts are protected and ready for viewing.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            show_metrics()
            balance_df = pd.DataFrame(
                [
                    {"Account": "Savings Account", "Number": "987654321012", "Balance": money(st.session_state.main_balance)},
                    {"Account": "Wallet Account", "Number": "876543210987", "Balance": money(st.session_state.wallet_balance)},
                    {"Account": "Scholarship Account", "Number": "765432109876", "Balance": money(st.session_state.scholarship_balance)},
                ]
            )
            st.dataframe(balance_df, use_container_width=True, hide_index=True)
        else:
            render_result({"status": "Failed", "message": "Incorrect password. Balance enquiry blocked."})
    navigation_buttons("Go to Home", "Home", "Transaction History", "Transaction History")


def confirm_payment_page():
    # ---------- CONFIRM PAYMENT PAGE ----------
    st.header("Confirm Payment")
    pending = st.session_state.pending_payment
    if not pending:
        st.info("No payment is waiting for confirmation.")
        cols = st.columns(2)
        with cols[0]:
            page_button("Make Payment", "Make Payment")
        with cols[1]:
            page_button("Go to Home", "Home")
        return

    st.markdown(
        """
        <div class="soft-card">
            <h3>Payment details</h3>
            <p class="hint">Check the details, enter your UPI password, and continue. BB84/QBER verification starts only after password approval.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    details = pd.DataFrame(
        [
            {"Field": "Payment Type", "Value": pending["payment_type"]},
            {"Field": "Receiver", "Value": pending["receiver_name"]},
            {"Field": "Receiver Number", "Value": pending["receiver_account"]},
            {"Field": "Amount", "Value": money(pending["amount"])},
            {"Field": "Note", "Value": pending["note"]},
        ]
    )
    st.dataframe(details, use_container_width=True, hide_index=True)

    password = st.text_input("Enter UPI password", type="password", key="confirm_payment_password")
    cols = st.columns(2)
    with cols[0]:
        if st.button("Confirm and Verify Quantum Channel", type="primary"):
            if not verify_password(password):
                render_result({"status": "Failed", "message": "Incorrect UPI password. Payment was not sent for BB84 verification."})
                return
            payment = st.session_state.pending_payment
            st.session_state.pending_payment = None
            process_payment(
                payment["payment_type"],
                payment["receiver_name"],
                payment["receiver_account"],
                payment["amount"],
                payment["note"],
                password,
                source_key=payment["source_key"],
                destination_key=payment["destination_key"],
            )
    with cols[1]:
        if st.button("Cancel Payment"):
            st.session_state.pending_payment = None
            navigate_to("Make Payment")
            st.rerun()
    navigation_buttons("Go to Home", "Home", "Edit Payment", "Make Payment")


def history_page():
    # ---------- TRANSACTION HISTORY ----------
    st.header("Transaction History")
    txns = st.session_state.transactions
    if not txns:
        st.info("No transactions yet. Run two demo payments to show one successful case and one QBER attack failure.")
        navigation_buttons("Go to Home", "Home", "Make Payment", "Make Payment")
        return

    df = pd.DataFrame(txns)
    if "scenario" not in df.columns:
        df["scenario"] = "BB84 payment verification"
    display_df = df[["id", "time", "type", "receiver", "amount", "status", "qber", "scenario", "reason"]].copy()
    display_df["amount"] = display_df["amount"].map(money)
    display_df["qber"] = display_df["qber"].map(lambda value: f"{value:.2f}%")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    with st.expander("Encrypted payload records"):
        st.dataframe(df[["id", "encrypted_payload", "key_length", "balance_after"]], use_container_width=True, hide_index=True)
    navigation_buttons("Go to Home", "Home", "Graph Analysis", "Graph Analysis")


def receipt_page():
    # ---------- PAYMENT RECEIPT ----------
    st.header("Payment Bill")
    result = st.session_state.last_result
    if not result or "transaction" not in result:
        st.info("No payment bill is available yet. Make a payment first.")
        cols = st.columns(2)
        with cols[0]:
            page_button("Make Payment", "Make Payment")
        with cols[1]:
            page_button("Go to Home", "Home")
        return

    txn = result["transaction"]
    quantum = result.get("quantum") or st.session_state.last_quantum
    if txn["status"] == "Success":
        status_block = f"""
        <div class="coin-stage"><div class="coin">INR</div></div>
        <div class="success-animation">
            <div class="checkmark">OK</div>
            <div>
                <h3>Payment successful</h3>
                <p>{result['message']}</p>
            </div>
        </div>
        """
    else:
        status_block = f"""
        <div class="failure-animation">
            <div class="crossmark">X</div>
            <div>
                <h3>Payment failed</h3>
                <p>{result['message']}</p>
            </div>
        </div>
        """
    st.markdown(status_block, unsafe_allow_html=True)

    bill_df = pd.DataFrame(
        [
            {"Field": "Transaction ID", "Value": txn["id"]},
            {"Field": "Date and Time", "Value": txn["time"]},
            {"Field": "Payment Type", "Value": txn["type"]},
            {"Field": "Receiver", "Value": txn["receiver"]},
            {"Field": "Receiver Number", "Value": txn["account"]},
            {"Field": "Amount", "Value": money(txn["amount"])},
            {"Field": "Status", "Value": txn["status"]},
            {"Field": "Demo Scenario", "Value": txn.get("scenario", "BB84 payment verification")},
            {"Field": "Reason", "Value": txn["reason"]},
            {"Field": "QBER", "Value": f"{txn['qber']:.2f}%"},
            {"Field": "BB84 Key Generated", "Value": txn["shared_key_preview"]},
            {"Field": "Key Length", "Value": f"{txn['key_length']} bits"},
        ]
    )
    st.dataframe(bill_df, use_container_width=True, hide_index=True)

    if quantum:
        show_quantum_summary(quantum, result.get("encrypted_payload", txn["encrypted_payload"]))

    cols = st.columns(2)
    with cols[0]:
        page_button("Make Another Payment", "Make Payment")
    with cols[1]:
        page_button("Go to Home", "Home")


def graphs_page():
    # ---------- GRAPH ANALYSIS ----------
    st.header("Graph Analysis")
    txns = list(reversed(st.session_state.transactions))
    if not txns:
        st.info("Graphs will appear after transactions are made.")
        navigation_buttons("Go to Home", "Home", "Make Payment", "Make Payment")
        return

    df = pd.DataFrame(txns)
    df["Attempt"] = range(1, len(df) + 1)
    df["Secure Limit"] = QBER_THRESHOLD

    # ---------- GRAPH STYLING ----------
    def style_plot(fig):
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8fff9"),
            title=dict(font=dict(color="#e8fff9", size=20), x=0.03),
            legend=dict(font=dict(color="#e8fff9")),
            xaxis=dict(
                title_font=dict(color="#e8fff9"),
                tickfont=dict(color="#d8fff7"),
                gridcolor="rgba(94, 234, 212, 0.14)",
                zerolinecolor="rgba(94, 234, 212, 0.18)",
            ),
            yaxis=dict(
                title_font=dict(color="#e8fff9"),
                tickfont=dict(color="#d8fff7"),
                gridcolor="rgba(94, 234, 212, 0.14)",
                zerolinecolor="rgba(94, 234, 212, 0.18)",
            ),
        )
        return fig

    cols = st.columns(2)
    with cols[0]:
        fig = px.line(df, x="Attempt", y=["qber", "Secure Limit"], markers=True, title="QBER Trend Per Transaction")
        style_plot(fig)
        st.plotly_chart(fig, use_container_width=True)
    with cols[1]:
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig = px.pie(status_counts, names="Status", values="Count", title="Success vs Failed Payments", hole=0.45)
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8fff9"),
            title=dict(font=dict(color="#e8fff9", size=20), x=0.03),
            legend=dict(font=dict(color="#e8fff9")),
        )
        st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(2)
    with cols[0]:
        fig = px.bar(df, x="Attempt", y="amount", color="status", title="Transaction Amounts")
        style_plot(fig)
        st.plotly_chart(fig, use_container_width=True)
    with cols[1]:
        fig = px.area(df, x="Attempt", y="balance_after", title="Main Account Balance Trend")
        style_plot(fig)
        st.plotly_chart(fig, use_container_width=True)
    navigation_buttons("Go to Home", "Home", "Transaction History", "Transaction History")


def qr_page():
    st.header("Generate QR Code")
    st.markdown(
        '<p class="hint">Generate a shareable QR code for your UPI ID. Enter only the amount needed to pay.</p>',
        unsafe_allow_html=True,
    )
    profile = st.session_state.get("user_profile", DEFAULT_USER)
    upi = st.text_input("Your UPI ID", value=profile.get("upi", DEFAULT_USER["upi"]))
    amount = st.number_input("Amount to receive", min_value=1.0, value=500.0, step=100.0)

    qr_data = f"upi://pay?pa={upi}&am={amount:.2f}&cu=INR"
    if st.button("Generate QR Code", type="primary"):
        img = qrcode.make(qr_data)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        data = buffer.getvalue()
        st.image(data, caption=f"UPI QR for INR {amount:.2f}", width=260)
        st.download_button("Download QR Code", data, file_name="quantumpay_qr.png", mime="image/png")
    navigation_buttons()


def quantum_page():
    st.header("Quantum Security Demo")
    mode = st.radio("Simulation mode", ["Secure channel", "Eavesdropping attempt"], horizontal=True)
    if st.button("Run BB84 Simulation", type="primary"):
        quantum = bb84_simulation(forced_mode="attack" if mode == "Eavesdropping attempt" else "secure")
        st.session_state.last_quantum = quantum
        show_quantum_summary(quantum, "demo-payload")

    if st.session_state.last_quantum:
        st.subheader("Latest Quantum Result")
        show_quantum_summary(st.session_state.last_quantum, "latest-payload")
    navigation_buttons("Go to Home", "Home", "Make Payment", "Make Payment")


def project_video_page():
    # ---------- PROJECT VIDEO PAGE ----------
    st.header("Project Video")
    uploaded_music = st.file_uploader("", type=["mp3"], label_visibility="collapsed")
    if uploaded_music is not None:
        PROJECT_MUSIC_FILE.write_bytes(uploaded_music.read())
        st.success("Music uploaded. Generate the video again to include it.")

    if st.button("Generate / Refresh Video", type="primary"):
        with st.spinner("Rendering project video..."):
            try:
                completed = subprocess.run(
                    ["python", "generate_project_animation.py"],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).resolve().parent,
                )
                st.success("Video generated successfully.")
                if completed.stdout.strip():
                    st.caption(completed.stdout.strip())
            except subprocess.CalledProcessError as exc:
                st.error("Video generation failed.")
                if exc.stderr:
                    st.code(exc.stderr)

    video_path = PROJECT_VIDEO_WITH_MUSIC_FILE if PROJECT_VIDEO_WITH_MUSIC_FILE.exists() else PROJECT_VIDEO_FILE

    if video_path.exists():
        video_bytes = video_path.read_bytes()
        st.video(video_bytes)
        st.download_button(
            "Download MP4 Video",
            data=video_bytes,
            file_name=video_path.name,
            mime="video/mp4",
        )
    else:
        st.info("No video found yet. Click Generate / Refresh Video.")

    navigation_buttons("Go to Home", "Home", "Make Payment", "Make Payment")


def route():
    # ---------- APP ROUTING ----------
    pages = [
        "Home",
        "Make Payment",
        "Transfer Money",
        "Confirm Payment",
        "Balance Enquiry",
        "Payment Receipt",
        "Transaction History",
        "Graph Analysis",
        "Generate QR Code",
        "Quantum Security Demo",
        "Project Video",
    ]
    selected = st.sidebar.radio("Navigation", pages, index=pages.index(st.session_state.active_page))
    if selected != st.session_state.active_page:
        navigate_to(selected)
        st.rerun()

    show_topbar()
    top_cols = st.columns([5, 1])
    with top_cols[1]:
        if st.button("Logout", use_container_width=True):
            logout()

    page = st.session_state.active_page
    if page == "Home":
        show_home()
    elif page == "Make Payment":
        make_payment_page()
    elif page == "Transfer Money":
        transfer_money_page()
    elif page == "Confirm Payment":
        confirm_payment_page()
    elif page == "Balance Enquiry":
        balance_page()
    elif page == "Payment Receipt":
        receipt_page()
    elif page == "Transaction History":
        history_page()
    elif page == "Graph Analysis":
        graphs_page()
    elif page == "Generate QR Code":
        qr_page()
    elif page == "Quantum Security Demo":
        quantum_page()
    elif page == "Project Video":
        project_video_page()


def main():
    inject_styles()
    init_state()
    if st.session_state.logged_in:
        route()
    else:
        login_page()


if __name__ == "__main__":
    main()
