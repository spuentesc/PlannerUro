
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Urosim / Trocasense Planner", layout="wide")

DATA_DIR = Path(".")
TASKS_PATH = DATA_DIR / "tasks.csv"
PROTOTYPES_PATH = DATA_DIR / "prototypes.csv"
MILESTONES_PATH = DATA_DIR / "milestones.csv"
TEMPLATES_PATH = DATA_DIR / "task_templates.csv"
PEOPLE_PATH = DATA_DIR / "people.csv"

APP_PALETTE = ["#f6bd60", "#f7ede2", "#f5cac3", "#84a59d", "#f28482"]
CHART_PALETTE = ["#fbf8cc", "#fde4cf", "#ffcfd2", "#f1c0e8", "#cfbaf0", "#a3c4f3", "#90dbf4", "#8eecf5", "#98f5e1", "#b9fbc0"]
PROJECT_COLORS = {"Trocasense": "#e89b2d", "Urosim": "#4f8f87", "General": "#d96c6c"}
STATUS_COLORS = {"Not Started": "#dc2626", "In Progress": "#d97706", "Blocked": "#7c3aed", "Done": "#16a34a"}
STATUS_OPTIONS = ["Not Started", "In Progress", "Blocked", "Done"]
PRIORITY_OPTIONS = ["Low", "Medium", "High", "Critical"]

st.markdown(
    """
    <style>
    .stApp { background-color: white; color: #24323d; }
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px; }
    h1, h2, h3 { color: #24323d; }
    section[data-testid="stSidebar"] { background-color: #f7ede2; }
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff 0%, #fffaf7 100%);
        border: 1px solid #efdfd2;
        border-radius: 18px;
        padding: 0.8rem 1rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #5d6b74 !important;
        opacity: 1 !important;
        font-weight: 600;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #24323d !important;
        opacity: 1 !important;
        font-weight: 700;
    }
    .section-card {
        background: #ffffff;
        border: 1px solid #f0e2d6;
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin-bottom: 1rem;
    }
    .tiny-note { color: #64748b; font-size: 0.92rem; }
    .legend-chip {
        display: inline-block; padding: 0.18rem 0.65rem; border-radius: 999px; 
        color: white; font-size: 0.82rem; margin-right: 0.35rem; font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def parse_json_list(value):
    if isinstance(value, list):
        return [str(v) for v in value]
    if pd.isna(value) or value == "":
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(v) for v in parsed]
    except Exception:
        pass
    return [v.strip() for v in str(value).split(",") if v.strip()]

def dump_json_list(value):
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    return json.dumps(parse_json_list(value), ensure_ascii=False)

def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

@st.cache_data
def load_static():
    prototypes = read_csv(PROTOTYPES_PATH)
    milestones = read_csv(MILESTONES_PATH)
    templates = read_csv(TEMPLATES_PATH)
    people = read_csv(PEOPLE_PATH)
    if "DefaultOwners" in prototypes.columns:
        prototypes["DefaultOwners"] = prototypes["DefaultOwners"].apply(parse_json_list)
    milestones["Date"] = pd.to_datetime(milestones["Date"], errors="coerce")
    return prototypes, milestones, templates, people

def load_tasks():
    df = read_csv(TASKS_PATH)
    required = [
        "Project", "Prototype", "Stage", "Task", "Owners", "StartDate", "EndDate",
        "DurationDays", "Status", "Progress", "WeeklyUpdate", "Notes", "Priority",
        "LabRequired", "CreatedFromTemplate", "PinnedWeek1"
    ]
    for col in required:
        if col not in df.columns:
            df[col] = ""
    df["Owners"] = df["Owners"].apply(parse_json_list)
    df["StartDate"] = pd.to_datetime(df["StartDate"], errors="coerce")
    df["EndDate"] = pd.to_datetime(df["EndDate"], errors="coerce")
    df["DurationDays"] = pd.to_numeric(df["DurationDays"], errors="coerce").fillna(0)
    df["Progress"] = pd.to_numeric(df["Progress"], errors="coerce").fillna(0).clip(0, 100)
    df["Status"] = df["Status"].replace("", "Not Started")
    df["Priority"] = df["Priority"].replace("", "Medium")
    df["PinnedWeek1"] = df["PinnedWeek1"].astype(str).str.lower().isin(["true", "1", "yes"])
    return df

def save_tasks(df):
    out = df.copy()
    out["Owners"] = out["Owners"].apply(dump_json_list)
    out["StartDate"] = pd.to_datetime(out["StartDate"], errors="coerce").dt.strftime("%Y-%m-%d")
    out["EndDate"] = pd.to_datetime(out["EndDate"], errors="coerce").dt.strftime("%Y-%m-%d")
    out.to_csv(TASKS_PATH, index=False)

def compute_duration_days(start, end):
    start = pd.to_datetime(start, errors="coerce")
    end = pd.to_datetime(end, errors="coerce")
    if pd.isna(start) or pd.isna(end):
        return 0
    return max((end - start).days + 1, 0)

def wrap_label(text, max_len=34):
    txt = str(text)
    if len(txt) <= max_len:
        return txt
    words = txt.split()
    lines = []
    cur = ""
    for w in words:
        cand = (cur + " " + w).strip()
        if len(cand) <= max_len:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return "<br>".join(lines)

prototypes, milestones, templates, people_df = load_static()
tasks = load_tasks()

tasks["OwnersLabel"] = tasks["Owners"].apply(lambda x: ", ".join(x))
tasks["DisplayTask"] = tasks.apply(lambda r: f"{r['Prototype']} • {r['Task']}", axis=1)

people_options = people_df["Person"].dropna().astype(str).tolist()
project_options = sorted(tasks["Project"].dropna().astype(str).unique().tolist())
prototype_options = sorted(tasks["Prototype"].dropna().astype(str).unique().tolist())

with st.sidebar:
    st.title("Planner controls")
    selected_projects = st.multiselect("Project", project_options, default=project_options)
    selected_prototypes = st.multiselect("Prototype", prototype_options, default=prototype_options)
    selected_people = st.multiselect("Owner", people_options, default=people_options)
    selected_status = st.multiselect("Status", STATUS_OPTIONS, default=STATUS_OPTIONS)
    timeline_color_mode = st.radio("Timeline colors", ["Project", "Status"], index=0)
    only_manual = st.checkbox("Only manual tasks", value=False)
    only_overdue = st.checkbox("Only overdue", value=False)

today = pd.Timestamp.today().normalize()
tasks["Overdue"] = tasks["EndDate"].notna() & (tasks["EndDate"] < today) & (tasks["Status"] != "Done")

filtered = tasks.copy()
if selected_projects:
    filtered = filtered[filtered["Project"].isin(selected_projects)]
if selected_prototypes:
    filtered = filtered[filtered["Prototype"].isin(selected_prototypes)]
if selected_status:
    filtered = filtered[filtered["Status"].isin(selected_status)]
if selected_people:
    filtered = filtered[filtered["Owners"].apply(lambda xs: any(p in xs for p in selected_people))]
if only_manual:
    filtered = filtered[filtered["CreatedFromTemplate"].astype(str).str.lower() == "manual"]
if only_overdue:
    filtered = filtered[filtered["Overdue"]]

st.title("Urosim / Trocasense Planner")
st.caption("Project planner with the full schedule preloaded from March 31 to May 27, editable task records, and a safer cloud-friendly editor.")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total tasks", int(len(filtered)))
m2.metric("Completed", int((filtered["Status"] == "Done").sum()))
m3.metric("In progress", int((filtered["Status"] == "In Progress").sum()))
m4.metric("Overdue", int(filtered["Overdue"].sum()))
m5.metric("Average progress", f"{round(filtered['Progress'].mean() if len(filtered) else 0, 1)}%")

st.markdown(
    f"""
    <div style="margin:0.35rem 0 0.9rem 0;">
      <span class="legend-chip" style="background:{STATUS_COLORS['Not Started']};">Not Started</span>
      <span class="legend-chip" style="background:{STATUS_COLORS['In Progress']};">In Progress</span>
      <span class="legend-chip" style="background:{STATUS_COLORS['Done']};">Done</span>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Master timeline", "Dashboard", "Task editor", "Weekly report", "Reference tables"])

with tab1:
    st.subheader("Master timeline")
    st.markdown('<div class="tiny-note">This chart uses larger labels, horizontal bars, and a simplified milestone display so the schedule is easier to read.</div>', unsafe_allow_html=True)

    timeline_df = filtered.dropna(subset=["StartDate", "EndDate"]).copy()
    if not timeline_df.empty:
        timeline_df = timeline_df.sort_values(["Project", "Prototype", "StartDate", "Task"]).copy()
        timeline_df["TaskLabel"] = timeline_df.apply(lambda r: wrap_label(f"{r['Prototype']} • {r['Task']}", 36), axis=1)

        color_col = "Project" if timeline_color_mode == "Project" else "Status"
        color_map = PROJECT_COLORS if color_col == "Project" else STATUS_COLORS
        fig = px.timeline(
            timeline_df,
            x_start="StartDate",
            x_end="EndDate",
            y="TaskLabel",
            color=color_col,
            color_discrete_map=color_map,
            hover_data=["Project", "Prototype", "Stage", "OwnersLabel", "Status", "Progress", "Notes"],
            height=max(700, 24 * len(timeline_df) + 220),
        )
        fig.update_yaxes(autorange="reversed", tickfont=dict(size=12))
        fig.update_xaxes(tickangle=0, tickfont=dict(size=12), showgrid=True, gridcolor="#e2e8f0")
        fig.update_layout(
            title="Full project schedule",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#334155", size=13),
            margin=dict(l=30, r=20, t=60, b=20),
            legend_title_text=color_col,
        )

        for _, row in milestones.dropna(subset=["Date"]).iterrows():
            fig.add_vline(x=row["Date"], line_dash="dot", line_color="#94a3b8", opacity=0.65)

        st.plotly_chart(fig, use_container_width=True)

        milestone_view = milestones.dropna(subset=["Date"]).copy()
        milestone_view["Date"] = milestone_view["Date"].dt.strftime("%Y-%m-%d")
        st.markdown("**Milestones**")
        st.dataframe(milestone_view, use_container_width=True, hide_index=True)

        proto_summary = (
            filtered.groupby(["Project", "Prototype"], dropna=False)
            .agg(Start=("StartDate", "min"), End=("EndDate", "max"), Tasks=("Task", "count"), AvgProgress=("Progress", "mean"))
            .reset_index()
            .sort_values(["Project", "Start"])
        )
        st.markdown("**Prototype schedule summary**")
        st.dataframe(proto_summary, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Dashboard")
    if len(filtered):
        left, right = st.columns(2)

        by_status = filtered.groupby("Status", dropna=False).size().reset_index(name="Count")
        fig1 = px.bar(
            by_status, x="Status", y="Count", title="Tasks by status",
            color="Status", color_discrete_map=STATUS_COLORS,
            text="Count"
        )
        fig1.update_layout(plot_bgcolor="white", paper_bgcolor="white", xaxis_title="", yaxis_title="Tasks")
        fig1.update_traces(textposition="outside")
        left.plotly_chart(fig1, use_container_width=True)

        by_proto = filtered.groupby("Prototype", dropna=False)["Progress"].mean().reset_index().sort_values("Progress", ascending=True)
        fig2 = px.bar(
            by_proto, x="Progress", y="Prototype", orientation="h",
            title="Average progress by prototype", color="Prototype",
            color_discrete_sequence=CHART_PALETTE, text="Progress"
        )
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False, xaxis_title="Average progress (%)", yaxis_title="")
        right.plotly_chart(fig2, use_container_width=True)

        a, b = st.columns(2)
        owner_load = filtered.explode("Owners")
        owner_load = owner_load[owner_load["Owners"].notna() & (owner_load["Owners"] != "")]
        owner_summary = owner_load.groupby("Owners").agg(Tasks=("Task", "count"), AvgProgress=("Progress", "mean")).reset_index().sort_values("Tasks", ascending=True)
        fig3 = px.bar(
            owner_summary, x="Tasks", y="Owners", orientation="h",
            title="Task load by owner", color="Owners", color_discrete_sequence=CHART_PALETTE, text="Tasks"
        )
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False, yaxis_title="", xaxis_title="Tasks")
        a.plotly_chart(fig3, use_container_width=True)

        week_view = filtered.copy()
        week_view["WeekStart"] = week_view["StartDate"].dt.to_period("W").apply(lambda r: r.start_time if pd.notna(r) else pd.NaT)
        week_summary = week_view.groupby("WeekStart", dropna=False).agg(Tasks=("Task", "count"), AvgProgress=("Progress", "mean")).reset_index().dropna()
        fig4 = px.line(week_summary, x="WeekStart", y="AvgProgress", markers=True, title="Average progress by week")
        fig4.update_traces(line_color="#4f8f87", marker_color="#e89b2d", marker_size=9)
        fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white", yaxis_title="Average progress (%)", xaxis_title="")
        b.plotly_chart(fig4, use_container_width=True)

        overdue_df = filtered[filtered["Overdue"]].copy()
        st.markdown("**Overdue tasks**")
        if overdue_df.empty:
            st.success("No overdue tasks in the current filtered view.")
        else:
            st.dataframe(
                overdue_df[["Project", "Prototype", "Task", "OwnersLabel", "EndDate", "Status", "Progress"]],
                use_container_width=True, hide_index=True
            )

with tab3:
    st.subheader("Task editor")
    st.markdown('<div class="tiny-note">I replaced the unstable in-table multi-owner widget with a safer two-part editor: a stable table for dates/status/progress and a row editor with a real multiselect for owners. This avoids the Streamlit Cloud crash.</div>', unsafe_allow_html=True)

    display_cols = ["Project", "Prototype", "Stage", "Task", "OwnersLabel", "StartDate", "EndDate", "DurationDays", "Status", "Progress", "Priority", "WeeklyUpdate", "Notes", "LabRequired", "CreatedFromTemplate"]
    table_df = filtered[display_cols].copy().rename(columns={"OwnersLabel": "Owners"})
    edited = st.data_editor(
        table_df,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "Project": st.column_config.SelectboxColumn("Project", options=project_options),
            "Prototype": st.column_config.SelectboxColumn("Prototype", options=prototype_options),
            "Owners": st.column_config.TextColumn("Owners", help="Use the detailed editor below to pick multiple owners safely."),
            "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS),
            "Priority": st.column_config.SelectboxColumn("Priority", options=PRIORITY_OPTIONS),
            "StartDate": st.column_config.DateColumn("Start date", format="YYYY-MM-DD"),
            "EndDate": st.column_config.DateColumn("End date", format="YYYY-MM-DD"),
            "DurationDays": st.column_config.NumberColumn("Duration (days)", min_value=0, step=1),
            "Progress": st.column_config.NumberColumn("Progress (%)", min_value=0, max_value=100, step=5),
            "WeeklyUpdate": st.column_config.TextColumn("Weekly update"),
            "Notes": st.column_config.TextColumn("Notes"),
            "LabRequired": st.column_config.SelectboxColumn("Lab required", options=["", "Yes"]),
        },
        key="stable_editor_v4",
    )

    if st.button("Save table changes"):
        current = tasks.copy()
        edited_save = edited.copy()
        edited_save["StartDate"] = pd.to_datetime(edited_save["StartDate"], errors="coerce")
        edited_save["EndDate"] = pd.to_datetime(edited_save["EndDate"], errors="coerce")
        edited_save["Progress"] = pd.to_numeric(edited_save["Progress"], errors="coerce").fillna(0).clip(0, 100)
        edited_save["DurationDays"] = [compute_duration_days(s, e) for s, e in zip(edited_save["StartDate"], edited_save["EndDate"])]
        edited_save["Owners"] = edited_save["Owners"].apply(parse_json_list)

        save_cols = ["Project", "Prototype", "Stage", "Task", "Owners", "StartDate", "EndDate", "DurationDays", "Status", "Progress", "WeeklyUpdate", "Notes", "Priority", "LabRequired", "CreatedFromTemplate"]
        edited_save = edited_save.rename(columns={"Owners": "Owners"})
        non_visible = current.loc[~current.index.isin(filtered.index), :]
        # align edited rows back to full schema
        merged = pd.concat([non_visible, edited_save], ignore_index=True)
        for col in current.columns:
            if col not in merged.columns:
                merged[col] = current[col].iloc[0] if len(current[col]) else ""
        save_tasks(merged[current.columns])
        st.success("Table changes saved to tasks.csv")

    st.markdown("### Detailed row editor")
    row_options = [f"{i} | {row['Prototype']} | {row['Task']}" for i, row in filtered.reset_index().iterrows()]
    if row_options:
        selected_row_label = st.selectbox("Select a task to edit in detail", row_options)
        selected_original_index = int(selected_row_label.split(" | ")[0])
        row = tasks.loc[selected_original_index].copy()

        c1, c2, c3 = st.columns(3)
        new_status = c1.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(row["Status"]) if row["Status"] in STATUS_OPTIONS else 0, key="detail_status")
        new_progress = c2.slider("Progress (%)", 0, 100, int(row["Progress"]), 5, key="detail_progress")
        new_priority = c3.selectbox("Priority", PRIORITY_OPTIONS, index=PRIORITY_OPTIONS.index(row["Priority"]) if row["Priority"] in PRIORITY_OPTIONS else 1, key="detail_priority")

        d1, d2 = st.columns(2)
        new_start = d1.date_input("Start date", value=row["StartDate"].date() if pd.notna(row["StartDate"]) else pd.Timestamp.today().date(), key="detail_start")
        new_end = d2.date_input("End date", value=row["EndDate"].date() if pd.notna(row["EndDate"]) else pd.Timestamp.today().date(), key="detail_end")

        new_owners = st.multiselect("Owners", people_options, default=[o for o in row["Owners"] if o in people_options], key="detail_owners")
        new_update = st.text_input("Weekly update", value=str(row["WeeklyUpdate"]), key="detail_update")
        new_notes = st.text_area("Notes", value=str(row["Notes"]), key="detail_notes")
        new_lab = st.selectbox("Lab required", ["", "Yes"], index=1 if str(row["LabRequired"]) == "Yes" else 0, key="detail_lab")

        if st.button("Save detailed row changes"):
            tasks.loc[selected_original_index, "Status"] = new_status
            tasks.loc[selected_original_index, "Progress"] = new_progress
            tasks.loc[selected_original_index, "Priority"] = new_priority
            tasks.loc[selected_original_index, "StartDate"] = pd.to_datetime(new_start)
            tasks.loc[selected_original_index, "EndDate"] = pd.to_datetime(new_end)
            tasks.loc[selected_original_index, "DurationDays"] = compute_duration_days(new_start, new_end)
            tasks.loc[selected_original_index, "Owners"] = new_owners
            tasks.loc[selected_original_index, "OwnersLabel"] = ", ".join(new_owners)
            tasks.loc[selected_original_index, "WeeklyUpdate"] = new_update
            tasks.loc[selected_original_index, "Notes"] = new_notes
            tasks.loc[selected_original_index, "LabRequired"] = new_lab
            save_tasks(tasks)
            st.success("Detailed changes saved.")

    with st.expander("Add a manual mini-task"):
        with st.form("manual_task_v4"):
            c1, c2, c3 = st.columns(3)
            project = c1.selectbox("Project", project_options)
            prototype = c2.selectbox("Prototype", prototype_options)
            priority = c3.selectbox("Priority", PRIORITY_OPTIONS, index=1)
            stage = st.text_input("Stage / general activity", value="General")
            task_name = st.text_input("Task name")
            owners = st.multiselect("Owners", people_options)
            d1, d2, d3 = st.columns(3)
            start = d1.date_input("Start date", key="manual_start")
            end = d2.date_input("End date", key="manual_end")
            status = d3.selectbox("Initial status", STATUS_OPTIONS, key="manual_status")
            weekly_update = st.text_input("Weekly update", key="manual_update")
            notes = st.text_area("Notes", key="manual_notes")
            lab_required = st.selectbox("Lab required?", ["", "Yes"], key="manual_lab")
            submitted = st.form_submit_button("Add task")

            if submitted and task_name:
                progress_seed = 100 if status == "Done" else (35 if status == "In Progress" else 0)
                row = {
                    "Project": project,
                    "Prototype": prototype,
                    "Stage": stage,
                    "Task": task_name,
                    "Owners": owners,
                    "StartDate": pd.to_datetime(start),
                    "EndDate": pd.to_datetime(end),
                    "DurationDays": compute_duration_days(start, end),
                    "Status": status,
                    "Progress": progress_seed,
                    "WeeklyUpdate": weekly_update,
                    "Notes": notes,
                    "Priority": priority,
                    "LabRequired": lab_required,
                    "CreatedFromTemplate": "Manual",
                    "PinnedWeek1": False,
                }
                tasks_new = pd.concat([tasks, pd.DataFrame([row])], ignore_index=True)
                save_tasks(tasks_new)
                st.success("Manual mini-task added. Refresh the app if needed.")

with tab4:
    st.subheader("Weekly report")
    report_df = filtered.copy()
    report_df["WeekStart"] = report_df["StartDate"].dt.to_period("W").apply(lambda r: r.start_time if pd.notna(r) else pd.NaT)
    available_weeks = sorted(report_df["WeekStart"].dropna().dt.strftime("%Y-%m-%d").unique().tolist())

    selected_week = st.selectbox("Reference week (week start)", available_weeks if available_weeks else [""])
    if selected_week:
        week_start = pd.to_datetime(selected_week)
        week_end = week_start + pd.Timedelta(days=6)
        week_tasks = report_df[(report_df["StartDate"] <= week_end) & (report_df["EndDate"] >= week_start)].copy()
        week_tasks["OwnersLabel"] = week_tasks["Owners"].apply(lambda x: ", ".join(x))

        k1, k2, k3 = st.columns(3)
        k1.metric("Active tasks", int(len(week_tasks)))
        k2.metric("Completed", int((week_tasks["Status"] == "Done").sum()))
        k3.metric("Average progress", f"{round(week_tasks['Progress'].mean() if len(week_tasks) else 0,1)}%")

        st.dataframe(
            week_tasks[["Project", "Prototype", "Task", "OwnersLabel", "Status", "Progress", "WeeklyUpdate", "Notes"]],
            use_container_width=True, hide_index=True
        )

with tab5:
    st.subheader("Reference tables")
    r1, r2 = st.columns(2)
    with r1:
        proto_ref = prototypes.copy()
        proto_ref["DefaultOwners"] = proto_ref["DefaultOwners"].apply(lambda x: ", ".join(x))
        st.markdown("**Prototype owners**")
        st.dataframe(proto_ref[["Project", "Prototype", "DefaultOwners", "Notes"]], use_container_width=True, hide_index=True)
    with r2:
        st.markdown("**Milestones**")
        st.dataframe(milestones.sort_values("Date"), use_container_width=True, hide_index=True)

    st.markdown("**Master activity library**")
    st.dataframe(templates, use_container_width=True, hide_index=True)

st.divider()
st.markdown("App palette: `['#f6bd60', '#f7ede2', '#f5cac3', '#84a59d', '#f28482']` with higher-contrast accents for readability.")
st.markdown("Chart palette: `['#fbf8cc', '#fde4cf', '#ffcfd2', '#f1c0e8', '#cfbaf0', '#a3c4f3', '#90dbf4', '#8eecf5', '#98f5e1', '#b9fbc0']`.")
