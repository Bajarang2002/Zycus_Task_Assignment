import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Zycus AI Support Triage",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f9fc;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    div.stButton > button {
        height: 45px;
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Zycus AI Support Triage")

st.caption(
    "Intelligent customer support ticket classification "
    "using Gemini and Retrieval-Augmented Generation."
)

st.divider()

st.header("Customer Ticket")

subject = st.text_input(
    "Ticket Subject",
    placeholder="e.g. Dashboard loads slowly",
)

body = st.text_area(
    "Ticket Description",
    height=160,
    placeholder=(
        "Describe the customer issue, impact, error message, "
        "affected users, and when the issue started."
    ),
)

st.header("Ticket Context")

col1, col2, col3 = st.columns(3)

with col1:
    product = st.text_input(
        "Product",
        placeholder="e.g. AnalyticsHub",
    )

with col2:
    product_area = st.text_input(
        "Product Area",
        placeholder="e.g. Dashboard",
    )

with col3:
    plan_tier = st.text_input(
        "Plan Tier",
        placeholder="e.g. Business",
    )

st.write("")

analyze = st.button(
    "Analyze Support Ticket",
    type="primary",
    use_container_width=True,
)

if analyze:
    if not subject.strip():
        st.warning("Please enter the ticket subject.")
        st.stop()

    if not body.strip():
        st.warning("Please enter the ticket description.")
        st.stop()

    payload = {
        "subject": subject.strip(),
        "body": body.strip(),
        "product": product.strip() or None,
        "product_area": product_area.strip() or None,
        "plan_tier": plan_tier.strip() or None,
    }

    try:
        with st.spinner(
            "Analyzing ticket and retrieving knowledge-base evidence..."
        ):
            response = requests.post(
                f"{API_URL}/triage",
                json=payload,
                timeout=180,
            )

        if response.status_code != 200:
            try:
                error_data = response.json()
                error_message = error_data.get(
                    "detail",
                    "Unknown API error.",
                )
            except Exception:
                error_message = response.text

            st.error(
                f"API Error ({response.status_code}): "
                f"{error_message}"
            )
            st.stop()

        result = response.json()

    except requests.exceptions.ConnectionError:
        st.error(
            "Unable to connect to the FastAPI server."
        )
        st.code(
            "python -m uvicorn main:app --reload"
        )
        st.stop()

    except requests.exceptions.Timeout:
        st.error(
            "The request timed out. Please try again."
        )
        st.stop()

    except requests.exceptions.RequestException as exc:
        st.error(f"Request failed: {exc}")
        st.stop()

    except ValueError:
        st.error(
            "The API returned an invalid JSON response."
        )
        st.stop()

    st.divider()
    st.header("Triage Decision")

    detected_product_area = result.get(
        "product_area",
        "Unknown",
    )

    issue_category = result.get(
        "issue_category",
        "Unknown",
    )

    urgency = result.get(
        "urgency",
        "Unknown",
    )

    known_issue = result.get(
        "known_issue",
        False,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Product Area",
            detected_product_area,
        )

    with col2:
        st.metric(
            "Issue Category",
            issue_category,
        )

    with col3:
        st.metric(
            "Urgency",
            urgency,
        )

    with col4:
        st.metric(
            "Known Issue",
            "Yes" if known_issue else "No",
        )

    references = result.get(
        "knowledge_base_references",
        [],
    )

    if known_issue and references:
        st.success(
            "Knowledge Base Match Confirmed"
        )
    else:
        st.info(
            "No direct Knowledge Base match was confirmed."
        )

    st.header("Analysis")

    reasoning = result.get(
        "reasoning",
        "No reasoning was returned.",
    )

    st.write(reasoning)

    st.header("Recommended Team")

    recommended_team = result.get(
        "recommended_team",
        "Not specified",
    )

    st.success(recommended_team)

    st.header("Recommended First Response")

    first_response = result.get(
        "first_response",
        "No response generated.",
    )

    st.text_area(
        "Customer-facing response",
        value=first_response,
        height=180,
        label_visibility="collapsed",
    )

    st.header("Knowledge Base Evidence")

    if references:
        st.caption(
            f"{len(references)} relevant knowledge-base "
            f"document(s) retrieved."
        )

        for ref in references:
            source = ref.get(
                "source",
                "Unknown source",
            )

            relevance = float(
                ref.get(
                    "relevance",
                    0,
                )
            )

            with st.container(border=True):
                st.write(f"**{source}**")

                st.caption(
                    f"Relevance score: {relevance:.2f}"
                )

                st.progress(
                    min(
                        max(relevance, 0.0),
                        1.0,
                    )
                )
    else:
        st.warning(
            "No knowledge-base references were returned."
        )

    st.header("Ticket Details")

    detail_col1, detail_col2, detail_col3 = st.columns(3)

    with detail_col1:
        st.write(
            f"**Product:** "
            f"{product or 'Not provided'}"
        )

    with detail_col2:
        st.write(
            f"**Product Area:** "
            f"{product_area or 'Not provided'}"
        )

    with detail_col3:
        st.write(
            f"**Plan Tier:** "
            f"{plan_tier or 'Not provided'}"
        )

    with st.expander("View Raw API Response"):
        st.json(result)

st.divider()

st.caption(
    "Zycus AI Support Triage | Gemini + ChromaDB RAG"
)