import streamlit as st
import pandas as pd
import datetime
import json
import os

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SIMATS Faculty Recruitment Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #0d2144 100%);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label { color: #94a3b8 !important; font-size: 0.8rem; }

/* KPI Cards */
.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    border-left: 5px solid #1e40af;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    margin-bottom: 8px;
}
.kpi-card.green  { border-left-color: #16a34a; }
.kpi-card.amber  { border-left-color: #d97706; }
.kpi-card.red    { border-left-color: #dc2626; }
.kpi-card.purple { border-left-color: #7c3aed; }
.kpi-number { font-size: 2.2rem; font-weight: 800; color: #0f172a; line-height: 1; }
.kpi-label  { font-size: 0.78rem; font-weight: 600; color: #64748b; margin-top: 4px; text-transform: uppercase; letter-spacing: .05em; }

/* Section header */
.section-header {
    font-size: 1.1rem; font-weight: 700; color: #0f172a;
    border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 16px;
}

/* Badge pills */
.badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: .04em;
}
.badge-open      { background:#dbeafe; color:#1d4ed8; }
.badge-shortlist { background:#fef3c7; color:#b45309; }
.badge-offered   { background:#d1fae5; color:#065f46; }
.badge-closed    { background:#f1f5f9; color:#475569; }
.badge-hold      { background:#fce7f3; color:#9d174d; }

/* Dataframe tweaks */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* Form card */
.form-card {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 24px; margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Data store (session state) ──────────────────────────────────────────────────
INSTITUTIONS = ["SIMATS Engineering", "SCAD", "SCLAS", "SPIER", "All"]
DEPARTMENTS  = [
    "CSE (AI & ML)", "CSE", "ECE", "EEE", "Mechanical", "Civil",
    "IT", "MBA", "MCA", "Mathematics", "Physics", "Chemistry",
    "English", "Hotel Management", "Design", "Other"
]
STATUS_OPTIONS = ["Open", "Shortlisted", "Interview Scheduled", "Offered", "Joined", "On Hold", "Closed"]
DESIGNATION    = ["Assistant Professor", "Associate Professor", "Professor", "HOD", "Dean", "Lab Instructor"]

STATUS_COLOR = {
    "Open": "badge-open",
    "Shortlisted": "badge-shortlist",
    "Interview Scheduled": "badge-shortlist",
    "Offered": "badge-offered",
    "Joined": "badge-offered",
    "On Hold": "badge-hold",
    "Closed": "badge-closed",
}

def init_data():
    if "vacancies" not in st.session_state:
        st.session_state.vacancies = pd.DataFrame([
            {
                "ID": "VAC-001", "Institution": "SIMATS Engineering", "Department": "CSE (AI & ML)",
                "Designation": "Associate Professor", "Positions": 3, "Filled": 1,
                "Posted Date": "2026-01-10", "Closing Date": "2026-06-30",
                "Status": "Open", "Remarks": "Urgent requirement"
            },
            {
                "ID": "VAC-002", "Institution": "SCAD", "Department": "Design",
                "Designation": "Assistant Professor", "Positions": 2, "Filled": 2,
                "Posted Date": "2026-02-01", "Closing Date": "2026-05-31",
                "Status": "Joined", "Remarks": "Both candidates joined"
            },
            {
                "ID": "VAC-003", "Institution": "SCLAS", "Department": "English",
                "Designation": "Assistant Professor", "Positions": 1, "Filled": 0,
                "Posted Date": "2026-03-15", "Closing Date": "2026-07-15",
                "Status": "Shortlisted", "Remarks": "3 candidates shortlisted"
            },
            {
                "ID": "VAC-004", "Institution": "SPIER", "Department": "ECE",
                "Designation": "Professor", "Positions": 1, "Filled": 0,
                "Posted Date": "2026-04-01", "Closing Date": "2026-08-01",
                "Status": "Interview Scheduled", "Remarks": "Interview on 25 May"
            },
            {
                "ID": "VAC-005", "Institution": "SIMATS Engineering", "Department": "Mechanical",
                "Designation": "Assistant Professor", "Positions": 4, "Filled": 0,
                "Posted Date": "2026-04-20", "Closing Date": "2026-09-30",
                "Status": "Open", "Remarks": ""
            },
        ])
    if "candidates" not in st.session_state:
        st.session_state.candidates = pd.DataFrame([
            {
                "Candidate ID": "CAN-001", "Name": "Dr. Priya Ramesh", "Vacancy ID": "VAC-001",
                "Department": "CSE (AI & ML)", "Institution": "SIMATS Engineering",
                "Qualification": "Ph.D", "Experience (yrs)": 8,
                "Application Date": "2026-01-20", "Interview Date": "2026-02-10",
                "Stage": "Joined", "Contact": "9876543210", "Email": "priya@example.com", "Remarks": "Excellent profile"
            },
            {
                "Candidate ID": "CAN-002", "Name": "Mr. Karthik Selvam", "Vacancy ID": "VAC-003",
                "Department": "English", "Institution": "SCLAS",
                "Qualification": "M.Phil", "Experience (yrs)": 5,
                "Application Date": "2026-03-20", "Interview Date": "2026-05-28",
                "Stage": "Shortlisted", "Contact": "9123456780", "Email": "karthik@example.com", "Remarks": ""
            },
            {
                "Candidate ID": "CAN-003", "Name": "Dr. Anitha Sundaram", "Vacancy ID": "VAC-004",
                "Department": "ECE", "Institution": "SPIER",
                "Qualification": "Ph.D", "Experience (yrs)": 12,
                "Application Date": "2026-04-05", "Interview Date": "2026-05-25",
                "Stage": "Interview Scheduled", "Contact": "9988776655", "Email": "anitha@example.com", "Remarks": "Senior profile"
            },
        ])
    if "vac_counter" not in st.session_state:
        st.session_state.vac_counter = 6
    if "can_counter" not in st.session_state:
        st.session_state.can_counter = 4

init_data()

# ── Helpers ─────────────────────────────────────────────────────────────────────
def kpi(label, value, color="blue"):
    color_map = {"blue":"", "green":" green", "amber":" amber", "red":" red", "purple":" purple"}
    cls = color_map.get(color, "")
    st.markdown(f"""
    <div class="kpi-card{cls}">
        <div class="kpi-number">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>""", unsafe_allow_html=True)

def next_vac_id():
    n = st.session_state.vac_counter
    st.session_state.vac_counter += 1
    return f"VAC-{n:03d}"

def next_can_id():
    n = st.session_state.can_counter
    st.session_state.can_counter += 1
    return f"CAN-{n:03d}"

# ── Sidebar ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Faculty Tracker")
    st.markdown("**SIMATS Group of Institutions**")
    st.markdown("---")
    page = st.radio("Navigation", [
        "📊 Dashboard",
        "📋 Vacancies",
        "👤 Candidates",
        "➕ Add Vacancy",
        "➕ Add Candidate",
        "📈 Reports",
    ])
    st.markdown("---")
    st.markdown(f"<small>Today: {datetime.date.today().strftime('%d %b %Y')}</small>", unsafe_allow_html=True)

df_v = st.session_state.vacancies
df_c = st.session_state.candidates

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("📊 Recruitment Dashboard")
    st.caption("Live overview of vacancies and pipeline across all SIMATS institutions")

    total_pos  = int(df_v["Positions"].sum())
    filled_pos = int(df_v["Filled"].sum())
    open_vac   = int((df_v["Status"] == "Open").sum())
    total_cand = len(df_c)
    joined     = int((df_c["Stage"] == "Joined").sum())

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi("Total Vacancies", len(df_v), "blue")
    with c2: kpi("Open Positions", total_pos - filled_pos, "amber")
    with c3: kpi("Positions Filled", filled_pos, "green")
    with c4: kpi("Total Candidates", total_cand, "purple")
    with c5: kpi("Joined This Cycle", joined, "green")

    st.markdown("---")
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="section-header">Vacancy Status Breakdown</div>', unsafe_allow_html=True)
        status_counts = df_v["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        st.bar_chart(status_counts.set_index("Status"), width='stretch', color="#1e40af")

    with col_r:
        st.markdown('<div class="section-header">Positions by Institution</div>', unsafe_allow_html=True)
        inst_sum = df_v.groupby("Institution")[["Positions","Filled"]].sum().reset_index()
        inst_sum["Open"] = inst_sum["Positions"] - inst_sum["Filled"]
        st.dataframe(
            inst_sum[["Institution","Positions","Filled","Open"]],
            hide_index=True, width='stretch'
        )

    st.markdown('<div class="section-header">Recent Vacancies</div>', unsafe_allow_html=True)
    st.dataframe(df_v[["ID","Institution","Department","Designation","Positions","Filled","Status"]]
                 .head(5), hide_index=True, width='stretch')

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — VACANCIES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Vacancies":
    st.title("📋 Vacancy Management")

    col1, col2, col3 = st.columns(3)
    with col1:
        inst_filter = st.selectbox("Institution", ["All"] + INSTITUTIONS[:-1])
    with col2:
        dept_filter = st.selectbox("Department", ["All"] + DEPARTMENTS)
    with col3:
        status_filter = st.selectbox("Status", ["All"] + STATUS_OPTIONS)

    filtered = df_v.copy()
    if inst_filter   != "All": filtered = filtered[filtered["Institution"] == inst_filter]
    if dept_filter   != "All": filtered = filtered[filtered["Department"]  == dept_filter]
    if status_filter != "All": filtered = filtered[filtered["Status"]      == status_filter]

    st.markdown(f"**{len(filtered)} record(s) found**")
    st.dataframe(filtered, hide_index=True, width='stretch')

    st.markdown("---")
    st.markdown('<div class="section-header">Update Vacancy Status</div>', unsafe_allow_html=True)
    vac_ids = df_v["ID"].tolist()
    sel_id  = st.selectbox("Select Vacancy ID", vac_ids)
    row_idx = df_v[df_v["ID"] == sel_id].index[0]
    cur_status = df_v.at[row_idx, "Status"]

    col_a, col_b = st.columns(2)
    with col_a:
        new_status = st.selectbox("New Status", STATUS_OPTIONS,
                                     index=STATUS_OPTIONS.index(cur_status) if cur_status in STATUS_OPTIONS else 0)
    with col_b:
        new_filled = st.number_input("Positions Filled", min_value=0,
                                     max_value=int(df_v.at[row_idx,"Positions"]),
                                     value=int(df_v.at[row_idx,"Filled"]))
    new_remark = st.text_input("Remarks", value=df_v.at[row_idx,"Remarks"])

    if st.button("💾 Update Vacancy", type="primary"):
        st.session_state.vacancies.at[row_idx, "Status"]  = new_status
        st.session_state.vacancies.at[row_idx, "Filled"]  = new_filled
        st.session_state.vacancies.at[row_idx, "Remarks"] = new_remark
        st.success(f"✅ Vacancy {sel_id} updated successfully!")
        st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-header">Delete Vacancy</div>', unsafe_allow_html=True)
    del_id = st.selectbox("Select Vacancy to Delete", vac_ids, key="del_vac")
    if st.button("🗑️ Delete Selected Vacancy", type="secondary"):
        st.session_state.vacancies = df_v[df_v["ID"] != del_id].reset_index(drop=True)
        st.success(f"Vacancy {del_id} deleted.")
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 — CANDIDATES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👤 Candidates":
    st.title("👤 Candidate Pipeline")

    col1, col2 = st.columns(2)
    with col1:
        stage_filter = st.selectbox("Filter by Stage", ["All"] + STATUS_OPTIONS)
    with col2:
        dept_c_filter = st.selectbox("Filter by Department", ["All"] + DEPARTMENTS)

    filtered_c = df_c.copy()
    if stage_filter   != "All": filtered_c = filtered_c[filtered_c["Stage"]      == stage_filter]
    if dept_c_filter  != "All": filtered_c = filtered_c[filtered_c["Department"] == dept_c_filter]

    st.markdown(f"**{len(filtered_c)} candidate(s) found**")
    st.dataframe(filtered_c, hide_index=True, width='stretch')

    st.markdown("---")
    st.markdown('<div class="section-header">Update Candidate Stage</div>', unsafe_allow_html=True)
    if len(df_c) > 0:
        can_ids = df_c["Candidate ID"].tolist()
        sel_can = st.selectbox("Select Candidate", can_ids)
        can_idx = df_c[df_c["Candidate ID"] == sel_can].index[0]
        cur_stage = df_c.at[can_idx, "Stage"]

        col_x, col_y = st.columns(2)
        with col_x:
            new_stage = st.selectbox("New Stage", STATUS_OPTIONS,
                                     index=STATUS_OPTIONS.index(cur_stage) if cur_stage in STATUS_OPTIONS else 0)
        with col_y:
            new_int_date = st.date_input("Interview Date",
                value=datetime.date.today())
        new_c_remark = st.text_input("Remarks", value=df_c.at[can_idx,"Remarks"])

        if st.button("💾 Update Candidate", type="primary"):
            st.session_state.candidates.at[can_idx, "Stage"]          = new_stage
            st.session_state.candidates.at[can_idx, "Interview Date"] = str(new_int_date)
            st.session_state.candidates.at[can_idx, "Remarks"]        = new_c_remark
            st.success(f"✅ Candidate {sel_can} updated!")
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 4 — ADD VACANCY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Vacancy":
    st.title("➕ Add New Vacancy")
    st.markdown('<div class="form-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        v_inst   = st.selectbox("Institution *", INSTITUTIONS[:-1])
        v_dept   = st.selectbox("Department *", DEPARTMENTS)
        v_desig  = st.selectbox("Designation *", DESIGNATION)
        v_pos    = st.number_input("Number of Positions *", min_value=1, max_value=20, value=1)
    with col2:
        v_posted = st.date_input("Posted Date", datetime.date.today())
        v_close  = st.date_input("Closing Date", datetime.date.today() + datetime.timedelta(days=90))
        v_status = st.selectbox("Initial Status", STATUS_OPTIONS)
        v_remark = st.text_area("Remarks", height=80)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("✅ Save Vacancy", type="primary", use_container_width=True):
        new_id = next_vac_id()
        new_row = {
            "ID": new_id, "Institution": v_inst, "Department": v_dept,
            "Designation": v_desig, "Positions": v_pos, "Filled": 0,
            "Posted Date": str(v_posted), "Closing Date": str(v_close),
            "Status": v_status, "Remarks": v_remark
        }
        st.session_state.vacancies = pd.concat(
            [st.session_state.vacancies, pd.DataFrame([new_row])], ignore_index=True)
        st.success(f"🎉 Vacancy **{new_id}** added successfully!")
        st.balloons()
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 5 — ADD CANDIDATE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Candidate":
    st.title("➕ Add New Candidate")
    st.markdown('<div class="form-card">', unsafe_allow_html=True)

    vac_id_list = df_v["ID"].tolist()

    if not vac_id_list:
        st.warning("No vacancies available. Please add a vacancy first.")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        c_name    = st.text_input("Candidate Name *")
        c_vac     = st.selectbox("Vacancy Applied For *", vac_id_list)
        c_qual    = st.selectbox("Qualification", ["Ph.D", "M.Phil", "M.E/M.Tech", "MBA", "M.Sc", "Other"])
        c_exp     = st.number_input("Experience (years)", min_value=0, max_value=40, value=0)
        c_contact = st.text_input("Contact Number")
    with col2:
        c_email   = st.text_input("Email Address")
        c_app_dt  = st.date_input("Application Date", datetime.date.today())
        c_int_dt  = st.date_input("Interview Date (if scheduled)", datetime.date.today())
        c_stage   = st.selectbox("Current Stage", STATUS_OPTIONS)
        c_remark  = st.text_area("Remarks", height=80)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("✅ Save Candidate", type="primary", use_container_width=True):
        if not c_name.strip():
            st.error("Candidate name is required.")
        else:
            # Auto-fill dept and institution from vacancy
            vac_row  = df_v[df_v["ID"] == c_vac].iloc[0]
            new_can_id = next_can_id()
            new_can = {
                "Candidate ID": new_can_id, "Name": c_name, "Vacancy ID": c_vac,
                "Department": vac_row["Department"], "Institution": vac_row["Institution"],
                "Qualification": c_qual, "Experience (yrs)": c_exp,
                "Application Date": str(c_app_dt), "Interview Date": str(c_int_dt),
                "Stage": c_stage, "Contact": c_contact, "Email": c_email, "Remarks": c_remark
            }
            st.session_state.candidates = pd.concat(
                [st.session_state.candidates, pd.DataFrame([new_can])], ignore_index=True)
            st.success(f"🎉 Candidate **{new_can_id} – {c_name}** added successfully!")
            st.balloons()
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 6 — REPORTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Reports":
    st.title("📈 Recruitment Reports")

    tab1, tab2, tab3 = st.tabs(["By Institution", "By Department", "Candidate Funnel"])

    with tab1:
        inst_report = df_v.groupby("Institution").agg(
            Total_Vacancies=("ID","count"),
            Total_Positions=("Positions","sum"),
            Filled=("Filled","sum"),
        ).reset_index()
        inst_report["Open"] = inst_report["Total_Positions"] - inst_report["Filled"]
        inst_report["Fill Rate (%)"] = (inst_report["Filled"] / inst_report["Total_Positions"] * 100).round(1)
        st.dataframe(inst_report, hide_index=True, width='stretch')
        st.bar_chart(inst_report.set_index("Institution")[["Total_Positions","Filled"]])

    with tab2:
        dept_report = df_v.groupby("Department").agg(
            Vacancies=("ID","count"),
            Positions=("Positions","sum"),
            Filled=("Filled","sum"),
        ).reset_index()
        dept_report["Open"] = dept_report["Positions"] - dept_report["Filled"]
        st.dataframe(dept_report.sort_values("Positions", ascending=False),
                     hide_index=True, width='stretch')
        st.bar_chart(dept_report.set_index("Department")["Positions"])

    with tab3:
        funnel = df_c["Stage"].value_counts().reset_index()
        funnel.columns = ["Stage", "Count"]
        st.markdown("**Candidate Stage Distribution**")
        st.dataframe(funnel, hide_index=True, width='stretch')
        st.bar_chart(funnel.set_index("Stage"), width='stretch', color="#7c3aed")

        st.markdown("---")
        st.markdown("**All Candidates Summary**")
        summary_c = df_c[["Candidate ID","Name","Institution","Department","Stage","Qualification","Experience (yrs)","Interview Date"]]
        st.dataframe(summary_c, hide_index=True, width='stretch')
