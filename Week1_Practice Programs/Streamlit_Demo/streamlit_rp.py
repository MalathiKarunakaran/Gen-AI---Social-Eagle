import streamlit as st
import pandas as pd
from datetime import date

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="University Recruitment Vacancy Tracker",
    page_icon="🎓",
    layout="wide"
)

# -----------------------------
# TITLE
# -----------------------------
st.title("🎓 University Recruitment Vacancy Request & Tracker")
st.markdown("### Faculty Recruitment Management System")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Navigation")

menu = st.sidebar.radio(
    "Go To",
    [
        "Dashboard",
        "Create Vacancy Request",
        "Vacancy Tracker",
        "Candidate Tracker"
    ]
)

# -----------------------------
# SAMPLE DATA STORAGE
# -----------------------------
if "vacancies" not in st.session_state:
    st.session_state.vacancies = pd.DataFrame(columns=[
        "Department",
        "Position",
        "No_of_Vacancies",
        "Qualification",
        "Experience",
        "Salary",
        "Requested_By",
        "Request_Date",
        "Status"
    ])

if "candidates" not in st.session_state:
    st.session_state.candidates = pd.DataFrame(columns=[
        "Candidate_Name",
        "Department",
        "Applied_Position",
        "Interview_Date",
        "Status"
    ])

# -----------------------------
# DASHBOARD
# -----------------------------
if menu == "Dashboard":

    st.subheader("📊 Recruitment Dashboard")

    total_vacancies = len(st.session_state.vacancies)

    open_positions = len(
        st.session_state.vacancies[
            st.session_state.vacancies["Status"] == "Open"
        ]
    )

    closed_positions = len(
        st.session_state.vacancies[
            st.session_state.vacancies["Status"] == "Closed"
        ]
    )

    total_candidates = len(st.session_state.candidates)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Vacancies", total_vacancies)
    col2.metric("Open Positions", open_positions)
    col3.metric("Closed Positions", closed_positions)
    col4.metric("Candidates", total_candidates)

    st.markdown("---")

    st.subheader("📌 Recent Vacancy Requests")

    st.dataframe(st.session_state.vacancies, use_container_width=True)

# -----------------------------
# CREATE VACANCY
# -----------------------------
elif menu == "Create Vacancy Request":

    st.subheader("📝 Create New Vacancy Request")

    with st.form("vacancy_form"):

        department = st.selectbox(
            "Department",
            [
                "CSE",
                "ECE",
                "EEE",
                "Mechanical",
                "Civil",
                "AI & DS",
                "MBA",
                "Science & Humanities"
            ]
        )

        position = st.selectbox(
            "Position",
            [
                "Assistant Professor",
                "Associate Professor",
                "Professor",
                "Lab Instructor",
                "Research Faculty"
            ]
        )

        no_of_vacancies = st.number_input(
            "Number of Vacancies",
            min_value=1,
            step=1
        )

        qualification = st.text_input(
            "Qualification Required"
        )

        experience = st.text_input(
            "Experience Required"
        )

        salary = st.text_input(
            "Salary Range"
        )

        requested_by = st.text_input(
            "Requested By"
        )

        request_date = st.date_input(
            "Request Date",
            value=date.today()
        )

        status = st.selectbox(
            "Status",
            [
                "Open",
                "Interview Ongoing",
                "Closed"
            ]
        )

        submit = st.form_submit_button("Submit Vacancy Request")

        if submit:

            new_row = pd.DataFrame([{
                "Department": department,
                "Position": position,
                "No_of_Vacancies": no_of_vacancies,
                "Qualification": qualification,
                "Experience": experience,
                "Salary": salary,
                "Requested_By": requested_by,
                "Request_Date": request_date,
                "Status": status
            }])

            st.session_state.vacancies = pd.concat(
                [st.session_state.vacancies, new_row],
                ignore_index=True
            )

            st.success("✅ Vacancy Request Created Successfully!")

# -----------------------------
# VACANCY TRACKER
# -----------------------------
elif menu == "Vacancy Tracker":

    st.subheader("📋 Vacancy Tracker")

    if len(st.session_state.vacancies) > 0:

        department_filter = st.selectbox(
            "Filter by Department",
            ["All"] + list(st.session_state.vacancies["Department"].unique())
        )

        if department_filter != "All":

            filtered_df = st.session_state.vacancies[
                st.session_state.vacancies["Department"] == department_filter
            ]

            st.dataframe(filtered_df, use_container_width=True)

        else:
            st.dataframe(
                st.session_state.vacancies,
                use_container_width=True
            )

    else:
        st.warning("No vacancy requests available.")

# -----------------------------
# CANDIDATE TRACKER
# -----------------------------
elif menu == "Candidate Tracker":

    st.subheader("👨‍🏫 Candidate Tracker")

    with st.form("candidate_form"):

        candidate_name = st.text_input("Candidate Name")

        department = st.selectbox(
            "Department ",
            [
                "CSE",
                "ECE",
                "EEE",
                "Mechanical",
                "Civil",
                "AI & DS",
                "MBA"
            ]
        )

        applied_position = st.selectbox(
            "Applied Position",
            [
                "Assistant Professor",
                "Associate Professor",
                "Professor",
                "Lab Instructor"
            ]
        )

        interview_date = st.date_input(
            "Interview Date",
            value=date.today()
        )

        candidate_status = st.selectbox(
            "Candidate Status",
            [
                "Applied",
                "Shortlisted",
                "Interview Scheduled",
                "Selected",
                "Rejected"
            ]
        )

        add_candidate = st.form_submit_button("Add Candidate")

        if add_candidate:

            candidate_row = pd.DataFrame([{
                "Candidate_Name": candidate_name,
                "Department": department,
                "Applied_Position": applied_position,
                "Interview_Date": interview_date,
                "Status": candidate_status
            }])

            st.session_state.candidates = pd.concat(
                [st.session_state.candidates, candidate_row],
                ignore_index=True
            )

            st.success("✅ Candidate Added Successfully!")

    st.markdown("---")

    st.subheader("📌 Candidate List")

    st.dataframe(
        st.session_state.candidates,
        use_container_width=True
    )