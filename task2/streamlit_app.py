import requests
import streamlit as st

API_URL="http://localhost:8000"

st.set_page_config(
    page_title="TAM Account Health",
    page_icon="📊",
    layout="wide",
)

st.title("TAM Account Health")
st.caption("Generate a concise and actionable account health brief with risks, ticket evidence, and TAM talking points.")

with st.form("account_form"):
    col1,col2=st.columns([4,1])
    with col1:
        account_id_input=st.text_input(
            "Account ID",
            placeholder="Example: ACC-3336",
        )
    with col2:
        st.write("")
        submitted=st.form_submit_button(
            "Generate Brief",
            type="primary",
            use_container_width=True,
        )

if submitted:
    account_id=account_id_input.strip()

    if not account_id:
        st.warning("Please enter an account ID.")
        st.stop()

    try:
        with st.spinner("Analyzing account health..."):
            response=requests.post(
                f"{API_URL}/account-health",
                json={"account_id":account_id},
                timeout=180,
            )

        if response.status_code!=200:
            try:
                error_data=response.json()
                error_message=error_data.get("detail",response.text)
            except Exception:
                error_message=response.text

            st.error(f"Unable to generate account brief: {error_message}")
            st.stop()

        result=response.json()

        st.divider()

        col1,col2=st.columns([3,1])

        with col1:
            st.subheader(result.get("company","Unknown Company"))
            st.caption(f"Account ID: {result.get('account_id',account_id)}")

        with col2:
            st.metric("90-Day Tickets",result.get("ticket_count_90d",0))

        st.header("1. Executive Summary")

        executive_summary=result.get(
            "executive_summary",
            "No executive summary available.",
        )

        st.write(executive_summary)

        st.header("2. Risks & Flagged Issues")

        risks=result.get(
            "open_risks_and_flagged_issues",
            [],
        )

        if not risks:
            st.info("No churn or escalation signals were detected in the available 90-day ticket data.")
        else:
            st.caption(f"{len(risks)} risk signal(s) detected")

            for index,risk in enumerate(risks,start=1):
                ticket_id=risk.get("ticket_id","Unknown")
                signal_type=risk.get("signal_type","Risk")
                severity=risk.get("severity","Unknown")
                reason=risk.get("reason","No reason provided.")
                evidence_quote=risk.get("evidence_quote","No direct evidence provided.")

                with st.container(border=True):
                    st.subheader(
                        f"{index}. {ticket_id} — "
                        f"{signal_type.replace('_',' ').title()}"
                    )

                    col1,col2=st.columns(2)

                    with col1:
                        st.write("**Severity**")
                        st.write(severity.title())

                    with col2:
                        st.write("**Ticket ID**")
                        st.write(ticket_id)

                    st.write("**Reason**")
                    st.write(reason)

                    st.write("**Direct Ticket Evidence**")
                    st.info(f'"{evidence_quote}"')

        st.header("3. Recommended TAM Talking Points")

        talking_points=result.get(
            "tam_talking_points",
            [],
        )

        if talking_points:
            for point in talking_points:
                st.write(f"• {point}")
        else:
            st.info("No specific talking points available.")

        st.header("4. Analysis Details")

        col1,col2,col3=st.columns(3)

        with col1:
            st.metric(
                "Tickets (90 Days)",
                result.get("ticket_count_90d",0),
            )

        with col2:
            st.metric("Risk Flags",len(risks))

        with col3:
            st.metric(
                "Account ID",
                result.get("account_id",account_id),
            )

        start_date=result.get("data_window_start","N/A")
        end_date=result.get("data_window_end","N/A")

        st.caption(f"Analysis window: {start_date} → {end_date}")

    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the FastAPI backend.")
        st.code("uvicorn main:app --reload",language="bash")

    except requests.exceptions.Timeout:
        st.error(
            "The request timed out. "
            "Please check whether the FastAPI backend is still processing the request."
        )

    except ValueError:
        st.error("The backend returned an invalid JSON response.")

    except Exception as error:
        st.error(f"Unexpected error: {error}")

st.divider()
st.caption("TAM Account Health • Account intelligence and risk summary")