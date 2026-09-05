import streamlit as st
import requests
import pandas as pd


# =========================================================
# CONFIG
# =========================================================

API_URL = "https://razorrecover-backend-nxq0.onrender.com/"

st.set_page_config(
    page_title="RazorRecover",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #0b1120;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    .hero {
        padding: 30px;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            #111827,
            #1e293b
        );
        border: 1px solid #334155;
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 17px;
        color: #94a3b8;
    }

    .metric-card {
        padding: 20px;
        border-radius: 15px;
        background: #111827;
        border: 1px solid #334155;
        min-height: 120px;
    }

    .metric-title {
        color: #94a3b8;
        font-size: 14px;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 700;
        margin-top: 8px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .status-success {
        padding: 12px;
        border-radius: 10px;
        background: #064e3b;
        color: #6ee7b7;
        font-weight: 600;
    }

    .status-danger {
        padding: 12px;
        border-radius: 10px;
        background: #450a0a;
        color: #fca5a5;
        font-weight: 600;
    }

    .status-warning {
        padding: 12px;
        border-radius: 10px;
        background: #451a03;
        color: #fcd34d;
        font-weight: 600;
    }

    .info-box {
        padding: 18px;
        border-radius: 12px;
        background: #111827;
        border: 1px solid #334155;
        margin-bottom: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "payment" not in st.session_state:
    st.session_state.payment = None

if "recovery" not in st.session_state:
    st.session_state.recovery = None

if "verification" not in st.session_state:
    st.session_state.verification = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "history" not in st.session_state:
    st.session_state.history = []


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    
            💰 RazorRecover
        
            AI-powered Revenue Recovery & Customer Payment Assistant
        
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ⚙️ Control Center")

    st.caption("RazorRecover Recovery Platform")

    st.divider()

    backend_status = False

    try:
        health = requests.get(
            f"{API_URL}/docs",
            timeout=2
        )

        backend_status = health.status_code == 200

    except Exception:
        backend_status = False

    if backend_status:

        st.success("🟢 Backend Online")

    else:

        st.error("🔴 Backend Offline")

    st.divider()

    st.markdown("### 📌 Workflow")

    st.write("1️⃣ Create failed payment")
    st.write("2️⃣ Analyze revenue risk")
    st.write("3️⃣ Identify root cause")
    st.write("4️⃣ AI chooses recovery")
    st.write("5️⃣ Guardrail validates action")
    st.write("6️⃣ Execute recovery")
    st.write("7️⃣ Verify payment")
    st.write("8️⃣ Customer assistance")

    st.divider()

    if st.button(
        "🗑️ Clear Session",
        use_container_width=True
    ):

        st.session_state.payment = None
        st.session_state.recovery = None
        st.session_state.verification = None
        st.session_state.chat_history = []
        st.session_state.history = []

        st.rerun()


# =========================================================
# KPI DASHBOARD
# =========================================================

st.markdown(
    '<div class="section-title">📊 Recovery Intelligence</div>',
    unsafe_allow_html=True
)

history = st.session_state.history

transactions_analyzed = len(history)

recovery_candidates = sum(
    1 for x in history
    if x.get("risk_score", 0) > 0
)

successful_recoveries = sum(
    1 for x in history
    if x.get("recovered", False)
)

revenue_at_risk = sum(
    x.get("amount", 0)
    for x in history
)

revenue_recovered = sum(
    x.get("amount_recovered", 0)
    for x in history
)

if revenue_at_risk > 0:

    recovery_rate = (
        revenue_recovered /
        revenue_at_risk
    ) * 100

else:

    recovery_rate = 0


col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Transactions",
        transactions_analyzed
    )


with col2:

    st.metric(
        "At Risk",
        recovery_candidates
    )


with col3:

    st.metric(
        "Revenue at Risk",
        f"₹{revenue_at_risk:,.0f}"
    )


with col4:

    st.metric(
        "Recovered",
        f"₹{revenue_recovered:,.0f}"
    )


with col5:

    st.metric(
        "Recovery Rate",
        f"{recovery_rate:.1f}%"
    )


st.divider()


# =========================================================
# CREATE PAYMENT
# =========================================================

st.markdown(
    '<div class="section-title">💳 Create Test Payment</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


with col1:

    customer_id = st.text_input(
        "Customer ID",
        value="DEMO_CUSTOMER_01"
    )

    amount = st.number_input(
        "Payment Amount (₹)",
        min_value=100.0,
        value=4999.0,
        step=100.0
    )


with col2:

    failure_reason = st.selectbox(
        "Simulate Payment Failure",
        [
            "insufficient_funds",
            "expired_card",
            "payment_declined",
            "network_timeout"
        ]
    )

    payment_type = st.selectbox(
        "Payment Type",
        [
            "payment",
            "subscription",
            "checkout"
        ]
    )


if st.button(
    "💳 Create Failed Payment",
    use_container_width=True
):

    payload = {
        "customer_id": customer_id,
        "amount": amount,
        "failure_reason": failure_reason,
        "payment_type": payment_type
    }

    try:

        response = requests.post(
            f"{API_URL}/recovery/payments/create",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:

            payment = response.json()

            st.session_state.payment = payment
            st.session_state.recovery = None
            st.session_state.verification = None
            st.session_state.chat_history = []

            st.success(
                f"Payment created successfully — "
                f"{payment['transaction_id']}"
            )

        else:

            st.error(response.text)

    except requests.exceptions.ConnectionError:

        st.error(
            "❌ FastAPI backend is not running."
        )

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )


# =========================================================
# PAYMENT STATUS
# =========================================================

if st.session_state.payment:

    payment = st.session_state.payment

    st.divider()

    st.markdown(
        '<div class="section-title">🚨 Payment At Risk</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Transaction",
            payment["transaction_id"]
        )


    with col2:

        st.metric(
            "Amount",
            f"₹{payment['amount']:,.0f}"
        )


    with col3:

        st.metric(
            "Status",
            payment["status"].upper()
        )


    with col4:

        st.metric(
            "Failure Reason",
            payment["failure_reason"]
        )


# =========================================================
# MAIN WORKSPACE
# =========================================================

if st.session_state.payment:

    st.divider()

    left, right = st.columns(
        [1.55, 1]
    )


    # =====================================================
    # LEFT — RECOVERY ENGINE
    # =====================================================

    with left:

        st.markdown(
            '<div class="section-title">'
            '🤖 Autonomous Recovery Engine'
            '</div>',
            unsafe_allow_html=True
        )

        if st.button(
            "🚀 Let RazorRecover Handle It",
            use_container_width=True
        ):

            transaction_id = (
                st.session_state.payment[
                    "transaction_id"
                ]
            )

            try:

                response = requests.post(
                    f"{API_URL}/recovery/"
                    f"transactions/"
                    f"{transaction_id}/recover",
                    timeout=30
                )

                if response.status_code == 200:

                    result = response.json()

                    st.session_state.recovery = result

                    risk = result.get(
                        "risk_analysis",
                        {}
                    )

                    guardrail = result.get(
                        "guardrail_decision",
                        {}
                    )

                    st.session_state.history.append(
                        {
                            "transaction_id":
                                transaction_id,

                            "amount":
                                payment["amount"],

                            "risk_score":
                                risk.get(
                                    "risk_score",
                                    0
                                ),

                            "action":
                                guardrail.get(
                                    "final_action",
                                    "UNKNOWN"
                                ),

                            "recovered":
                                False,

                            "amount_recovered":
                                0
                        }
                    )

                    st.success(
                        "✅ Transaction analyzed successfully."
                    )

                else:

                    st.error(
                        response.text
                    )

            except Exception as e:

                st.error(
                    f"Recovery error: {str(e)}"
                )


        # =================================================
        # DECISION TRACE
        # =================================================

        if st.session_state.recovery:

            result = st.session_state.recovery

            risk = result.get(
                "risk_analysis",
                {}
            )

            cause = result.get(
                "root_cause_analysis",
                {}
            )

            strategy = result.get(
                "recovery_strategy",
                {}
            )

            guardrail = result.get(
                "guardrail_decision",
                {}
            )

            execution = result.get(
                "execution_result",
                {}
            )


            st.markdown(
                '<div class="section-title">'
                '🧠 AI Decision Trace'
                '</div>',
                unsafe_allow_html=True
            )


            # ---------------------------------------------
            # RISK + ROOT CAUSE
            # ---------------------------------------------

            col1, col2 = st.columns(2)


            with col1:

                st.markdown(
                    "### 1️⃣ Revenue Risk"
                )

                risk_score = risk.get(
                    "risk_score",
                    0
                )

                st.metric(
                    "Risk Score",
                    risk_score
                )

                st.write(
                    "Risk Level:",
                    f"**{risk.get('risk_level', 'UNKNOWN')}**"
                )


            with col2:

                st.markdown(
                    "### 2️⃣ Root Cause"
                )

                st.write(
                    f"**{cause.get('root_cause', 'UNKNOWN')}**"
                )

                confidence = cause.get(
                    "confidence",
                    0
                )

                if confidence <= 1:

                    confidence *= 100

                st.write(
                    f"Confidence: **{confidence:.0f}%**"
                )


            # ---------------------------------------------
            # AI DECISION / GUARDRAIL / EXECUTION
            # ---------------------------------------------

            col1, col2, col3 = st.columns(3)


            with col1:

                st.markdown(
                    "### 3️⃣ AI Decision"
                )

                st.info(
                    strategy.get(
                        "action",
                        "NO_ACTION"
                    )
                )

                if strategy.get("reason"):

                    st.caption(
                        strategy["reason"]
                    )


            with col2:

                st.markdown(
                    "### 4️⃣ Guardrail"
                )

                if guardrail.get(
                    "allowed",
                    False
                ):

                    st.success(
                        "✓ ACTION ALLOWED"
                    )

                else:

                    st.error(
                        "✕ ACTION BLOCKED"
                    )

                st.caption(
                    guardrail.get(
                        "reason",
                        "No reason available"
                    )
                )


            with col3:

                st.markdown(
                    "### 5️⃣ Execution"
                )

                status = execution.get(
                    "status",
                    "UNKNOWN"
                )

                st.write(
                    f"**{status}**"
                )


            # =================================================
            # AI EXPLANATION
            # =================================================

            st.markdown(
                "### 💡 Why RazorRecover Chose This"
            )

            explanation = (
                strategy.get(
                    "reason"
                )
                or strategy.get(
                    "customer_message"
                )
                or cause.get(
                    "explanation"
                )
                or "Recovery action selected based on transaction risk and payment context."
            )

            st.info(explanation)


            # =================================================
            # RECOVERY ACTION
            # =================================================

            action = guardrail.get(
                "final_action"
            )


            if action == "SCHEDULE_RETRY":

                st.markdown(
                    "### 🔄 Recovery Action"
                )

                if st.button(
                    "⚡ Execute Retry",
                    use_container_width=True
                ):

                    transaction_id = (
                        st.session_state.payment[
                            "transaction_id"
                        ]
                    )

                    try:

                        response = requests.post(
                            f"{API_URL}/recovery/"
                            f"transactions/"
                            f"{transaction_id}/retry",
                            timeout=30
                        )

                        if response.status_code == 200:

                            verification = (
                                response.json()
                            )

                            st.session_state.verification = (
                                verification
                            )

                            recovery_data = (
                                verification.get(
                                    "recovery_verification",
                                    {}
                                )
                            )

                            if recovery_data.get(
                                "recovered",
                                False
                            ):

                                amount_recovered = (
                                    recovery_data.get(
                                        "amount_recovered",
                                        0
                                    )
                                )

                                # Update history
                                for item in reversed(
                                    st.session_state.history
                                ):

                                    if item[
                                        "transaction_id"
                                    ] == transaction_id:

                                        item[
                                            "recovered"
                                        ] = True

                                        item[
                                            "amount_recovered"
                                        ] = amount_recovered

                                        break

                                st.balloons()

                                st.success(
                                    "🎉 Payment recovered successfully!"
                                )

                            else:

                                st.warning(
                                    "Payment was not recovered."
                                )

                        else:

                            st.error(
                                response.text
                            )

                    except Exception as e:

                        st.error(
                            f"Retry error: {str(e)}"
                        )


            elif action == "REQUEST_PAYMENT_METHOD_UPDATE":

                st.warning(
                    "👤 Customer must update the payment method."
                )


            elif action == "ALTERNATIVE_PAYMENT_METHOD":

                st.info(
                    "💳 Customer should use an alternative payment method."
                )


            elif action == "ESCALATE_TO_SUPPORT":

                st.error(
                    "🚨 Recovery case requires merchant support."
                )


            # =================================================
            # RECOVERY RESULT
            # =================================================

            if st.session_state.verification:

                verification = (
                    st.session_state.verification
                )

                recovery_data = (
                    verification.get(
                        "recovery_verification",
                        {}
                    )
                )

                st.markdown(
                    "### 💰 Recovery Result"
                )

                col1, col2, col3 = st.columns(3)


                with col1:

                    st.metric(
                        "Payment Status",
                        verification.get(
                            "payment_status",
                            "UNKNOWN"
                        ).upper()
                    )


                with col2:

                    st.metric(
                        "Recovered",
                        "YES"
                        if recovery_data.get(
                            "recovered",
                            False
                        )
                        else "NO"
                    )


                with col3:

                    st.metric(
                        "₹ Recovered",
                        f"₹{recovery_data.get('amount_recovered', 0):,.0f}"
                    )


                if recovery_data.get(
                    "recovered",
                    False
                ):

                    st.success(
                        f"₹{recovery_data.get('amount_recovered', 0):,.0f} "
                        "successfully recovered."
                    )


    # =====================================================
    # RIGHT — CUSTOMER ASSISTANT
    # =====================================================

    with right:

        st.markdown(
            '<div class="section-title">'
            '💬 Customer Payment Assistant'
            '</div>',
            unsafe_allow_html=True
        )

        st.caption(
            f"Customer: {customer_id}"
        )


        chat_container = st.container(
            height=430
        )


        with chat_container:

            if not st.session_state.chat_history:

                st.info(
                    "👋 Hi! I'm RazorRecover. "
                    "Ask me anything about your payment."
                )


            for chat in st.session_state.chat_history:

                with st.chat_message(
                    chat["role"]
                ):

                    st.write(
                        chat["message"]
                    )


        message = st.chat_input(
            "Ask about your payment..."
        )


        if message:

            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "message": message
                }
            )


            try:

                response = requests.post(
                    f"{API_URL}/recovery/"
                    f"customers/"
                    f"{customer_id}/chat",
                    json={
                        "message": message
                    },
                    timeout=30
                )


                if response.status_code == 200:

                    data = response.json()

                    answer = data.get(
                        "response",
                        "I couldn't generate a response."
                    )

                else:

                    answer = (
                        "Sorry, I couldn't access "
                        "your payment information."
                    )


            except Exception:

                answer = (
                    "Payment assistant is currently "
                    "unavailable."
                )


            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "message": answer
                }
            )

            st.rerun()


# =========================================================
# RECOVERY HISTORY
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">'
    '📜 Recovery History'
    '</div>',
    unsafe_allow_html=True
)


if st.session_state.history:

    df = pd.DataFrame(
        st.session_state.history
    )

    display_df = df.rename(
        columns={
            "transaction_id": "Transaction",
            "amount": "Amount",
            "risk_score": "Risk Score",
            "action": "Recovery Action",
            "recovered": "Recovered",
            "amount_recovered": "Amount Recovered"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # CHARTS
    # =====================================================

    st.markdown(
        "### 📈 Recovery Performance"
    )

    chart_col1, chart_col2 = st.columns(2)


    with chart_col1:

        chart_data = pd.DataFrame(
            {
                "Metric": [
                    "Revenue at Risk",
                    "Revenue Recovered"
                ],

                "Amount": [
                    revenue_at_risk,
                    revenue_recovered
                ]
            }
        )

        st.bar_chart(
            chart_data.set_index(
                "Metric"
            )
        )


    with chart_col2:

        risk_data = pd.DataFrame(
            {
                "Transaction":
                    [
                        x["transaction_id"]
                        for x in history
                    ],

                "Risk Score":
                    [
                        x["risk_score"]
                        for x in history
                    ]
            }
        )

        if not risk_data.empty:

            st.line_chart(
                risk_data.set_index(
                    "Transaction"
                )
            )


else:

    st.info(
        "No recovery transactions yet. "
        "Create a failed payment to start."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "RazorRecover • AI-powered autonomous revenue recovery platform"
)
