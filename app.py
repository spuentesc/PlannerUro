
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
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

PROJECT_COLORS = {"Trocasense": "#f6bd60", "Urosim": "#84a59d", "General": "#f28482"}
PROJECT_LIGHT = {"Trocasense": "#fff4dd", "Urosim": "#eef8f6", "General": "#fff0f0"}
STATUS_COLORS = {"Not Started": "#dc2626", "In Progress": "#d97706", "Blocked": "#7c3aed", "Done": "#16a34a"}

STATUS_OPTIONS = ["Not Started", "In Progress", "Blocked", "Done"]
PRIORITY_OPTIONS = ["Low", "Medium", "High", "Critical"]

st.markdown(
    """
    <style>
    .stApp {
        background: white;
        color: #1f2937;
    }
    .block-container {
        max-width: 1550px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    section[data-testid="stSidebar"] {
        background: #f7ede2;
        border-right: 1px solid #eadbce;
    }
    h1, h2, h3 {
        color: #1f2937 !important;
        letter-spacing: -0.02em;
    }

    /* Stronger visibility for subtitles and labels */
    p, label, .small-note {
        color: #475569 !important;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff 0%, #fffaf7 100%);
        border: 1px solid #eadbce;
        border-radius: 18px;
        padding: 0.9rem 1rem;
        box-shadow: 0 8px 22px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricValue"] {
        color: #1f2937 !important;
        opacity: 1 !important;
    }

    /* Tabs */
    div[data-baseweb="tab-list"] {
        gap: 0.35rem;
        border-bottom: 1px solid #eadbce;
        margin-bottom: 0.6rem;
    }
    button[data-baseweb="tab"] {
        background: #f7ede2 !important;
        border: 1px solid #eadbce !important;
        border-bottom: none !important;
        border-radius: 12px 12px 0 0 !important;
        padding: 0.55rem 1rem !important;
    }
    button[data-baseweb="tab"] p {
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 0.96rem !important;
    }
    button[data-baseweb="tab"]:hover {
        background: #f5cac3 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: white !important;
        border: 1px solid #e89b2d !important;
        border-bottom: 3px solid #e89b2d !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #b45309 !important;
        font-weight: 700 !important;
    }

    /* Inputs/selects/multiselects */
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] > div,
    div[data-testid="stTextInputRootElement"] > div,
    div[data-testid="stDateInputField"] > div,
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stTextArea"] textarea {
        background: #fffdfb !important;
        color: #1f2937 !important;
        border: 1px solid #eadbce !important;
        border-radius: 14px !important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input,
    div[data-baseweb="base-input"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stDateInputField"] input {
        color: #1f2937 !important;
    }

    /* Pastel tags for multiselect/filter chips */
    div[data-baseweb="tag"] {
        color: #1f2937 !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
    }
    div[data-baseweb="tag"]:nth-of-type(5n+1) {
        background: #fbf8cc !important;
    }
    div[data-baseweb="tag"]:nth-of-type(5n+2) {
        background: #fde4cf !important;
    }
    div[data-baseweb="tag"]:nth-of-type(5n+3) {
        background: #ffcfd2 !important;
    }
    div[data-baseweb="tag"]:nth-of-type(5n+4) {
        background: #a3c4f3 !important;
    }
    div[data-baseweb="tag"]:nth-of-type(5n+5) {
        background: #b9fbc0 !important;
    }
    div[data-baseweb="tag"] span, div[data-baseweb="tag"] svg {
        color: #1f2937 !important;
        fill: #1f2937 !important;
    }

    .status-pill {
        display: inline-block;
        padding: 0.18rem 0.62rem;
        border-radius: 999px;
        color: white;
        font-weight: 700;
        font-size: 0.82rem;
        margin-right: 0.35rem;
    }
    .small-note {
        font-size: 0.92rem;
    }
    .roadmap-card {
        border: 1px solid #eadbce;
        border-radius: 18px;
        background: #fffdfb;
        padding: 0.85rem 0.95rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04);
        margin-bottom: 0.75rem;
    }
    .roadmap-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.25rem;
    }
    .roadmap-sub {
        font-size: 0.88rem;
        color: #64748b;
        margin-bottom: 0.35rem;
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
    lines, cur = [], ""
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

def status_pill(status: str):
    color = STATUS_COLORS.get(status, "#64748b")
    return f'<span class="status-pill" style="background:{color};">{status}</span>'

def fix_plotly_axes(fig):
    fig.update_xaxes(
        tickfont=dict(color="#1f2937", size=12),
        title_font=dict(color="#1f2937"),
        showgrid=True,
        gridcolor="#f1f5f9",
        zeroline=False,
    )
    fig.update_yaxes(
        tickfont=dict(color="#1f2937", size=12),
        title_font=dict(color="#1f2937"),
        showgrid=False,
    )
    fig.update_layout(
        font=dict(color="#1f2937"),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig

def render_plotly(container, fig, key: str):
    container.plotly_chart(
        fix_plotly_axes(fig),
        use_container_width=True,
        key=key,
    )

def build_week_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.dropna(subset=["StartDate", "EndDate"]).copy()
    out["WeekStart"] = out["StartDate"].dt.to_period("W").apply(
        lambda r: r.start_time if pd.notna(r) else pd.NaT
    )
    return out

def make_styled_table(df, project_col=None, font_size="12px"):
    def row_style(row):
        if project_col and project_col in row.index:
            base = PROJECT_LIGHT.get(row[project_col], "#fffdfb")
            return [f"background-color: {base}; color: #1f2937;"] * len(row)
        return ["background-color: #fffdfb; color: #1f2937;"] * len(row)

    styles = [
        {
            "selector": "th",
            "props": [
                ("background-color", "#f7ede2"),
                ("color", "#1f2937"),
                ("font-weight", "700"),
                ("border", "1px solid #eadbce"),
                ("padding", "6px 8px"),
                ("font-size", font_size),
                ("white-space", "normal"),
                ("word-break", "break-word"),
            ],
        },
        {
            "selector": "td",
            "props": [
                ("border", "1px solid #f0e6df"),
                ("padding", "6px 8px"),
                ("color", "#1f2937"),
                ("font-size", font_size),
                ("white-space", "normal"),
                ("word-break", "break-word"),
                ("vertical-align", "top"),
            ],
        },
        {
            "selector": "table",
            "props": [
                ("border-collapse", "collapse"),
                ("border-radius", "12px"),
                ("overflow", "hidden"),
                ("width", "100%"),
                ("table-layout", "fixed"),
            ],
        },
    ]
    return df.style.apply(row_style, axis=1).set_table_styles(styles)

prototypes, milestones, templates, people_df = load_static()
tasks = load_tasks()

tasks["OwnersLabel"] = tasks["Owners"].apply(lambda x: ", ".join(x))
tasks["Overdue"] = tasks["EndDate"].notna() & (tasks["EndDate"] < pd.Timestamp.today().normalize()) & (tasks["Status"] != "Done")

people_options = sorted(people_df["Person"].dropna().astype(str).tolist()) if "Person" in people_df.columns else []
project_options = sorted(tasks["Project"].dropna().astype(str).unique().tolist())
prototype_options = sorted(tasks["Prototype"].dropna().astype(str).unique().tolist())

with st.sidebar:
    st.title("Planner controls")
    selected_projects = st.multiselect("Project", project_options, default=project_options)
    selected_prototypes = st.multiselect("Prototype", prototype_options, default=prototype_options)
    selected_people = st.multiselect("Owner", people_options, default=people_options)
    selected_status = st.multiselect("Status", STATUS_OPTIONS, default=STATUS_OPTIONS)
    color_mode = st.radio("Timeline colors", ["Project", "Status"], index=0)
    only_manual = st.checkbox("Only manual tasks", value=False)
    only_overdue = st.checkbox("Only overdue", value=False)

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
st.caption("Product-style planner with timeline, roadmap by week, clean task views, and single-task editing.")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total tasks", int(len(filtered)))
m2.metric("Completed", int((filtered["Status"] == "Done").sum()))
m3.metric("In progress", int((filtered["Status"] == "In Progress").sum()))
m4.metric("Overdue", int(filtered["Overdue"].sum()))
m5.metric("Average progress", f"{round(filtered['Progress'].mean() if len(filtered) else 0, 1)}%")

st.markdown(
    f"""
    <div style="margin:0.3rem 0 1rem 0;">
      {status_pill("Not Started")}
      {status_pill("In Progress")}
      {status_pill("Done")}
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Master timeline", "Roadmap by week", "Dashboard", "Tasks table", "Task editor", "Weekly report"
])

with tab1:
    st.subheader("Master timeline")
    st.markdown('<div class="small-note">Readable timeline plus lighter, project-colored summary tables.</div>', unsafe_allow_html=True)

    timeline_df = filtered.dropna(subset=["StartDate", "EndDate"]).copy()
    if not timeline_df.empty:
        timeline_df = timeline_df.sort_values(["Project", "Prototype", "StartDate", "Task"]).copy()
        timeline_df["TaskLabel"] = timeline_df.apply(lambda r: wrap_label(f"{r['Prototype']} • {r['Task']}", 40), axis=1)

        color_col = "Project" if color_mode == "Project" else "Status"
        color_map = PROJECT_COLORS if color_col == "Project" else STATUS_COLORS

        fig = px.timeline(
            timeline_df,
            x_start="StartDate",
            x_end="EndDate",
            y="TaskLabel",
            color=color_col,
            color_discrete_map=color_map,
            hover_data=["Project", "Prototype", "Stage", "OwnersLabel", "Status", "Progress", "Notes"],
            height=max(750, 28 * len(timeline_df) + 240),
        )
        fig.update_yaxes(autorange="reversed", tickfont=dict(size=12, color="#1f2937"))
        fig.update_xaxes(tickangle=0, tickfont=dict(size=12, color="#1f2937"), showgrid=True, gridcolor="#f1f5f9", title="")
        fig.update_layout(
            title="Full project schedule",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#1f2937", size=13),
            legend_title_text=color_col,
            legend=dict(font=dict(color="#1f2937"), bgcolor="rgba(255,255,255,0.92)"),
            margin=dict(l=20, r=20, t=70, b=20),
        )

        for _, row in milestones.dropna(subset=["Date"]).iterrows():
            fig.add_vline(x=row["Date"], line_dash="dot", line_color="#94a3b8", opacity=0.7)

        render_plotly(st, fig, "master_timeline")

        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("**Milestones**")
            milestone_view = milestones.dropna(subset=["Date"]).copy()
            milestone_view["Date"] = pd.to_datetime(milestone_view["Date"], errors="coerce").dt.strftime("%b %d")
            st.table(make_styled_table(milestone_view, font_size="11px"))
        with c2:
            st.markdown("**Tasks by project / prototype**")
            proto_summary = (
                filtered.groupby(["Project", "Prototype"], dropna=False)
                .agg(Start=("StartDate", "min"), End=("EndDate", "max"), Tasks=("Task", "count"), AvgProgress=("Progress", "mean"))
                .reset_index()
                .sort_values(["Project", "Start"])
            )
            proto_summary["Start"] = pd.to_datetime(proto_summary["Start"], errors="coerce").dt.strftime("%b %d")
            proto_summary["End"] = pd.to_datetime(proto_summary["End"], errors="coerce").dt.strftime("%b %d")
            proto_summary["AvgProgress"] = proto_summary["AvgProgress"].round(1).astype(str) + "%"
            st.table(make_styled_table(proto_summary, project_col="Project", font_size="11px"))

with tab2:
    st.subheader("Roadmap by week")
    st.markdown('<div class="small-note">A cleaner product-style weekly roadmap so you can see what is happening each week without reading the full Gantt.</div>', unsafe_allow_html=True)

    week_df = build_week_df(filtered)
    if not week_df.empty:
        roadmap_weeks = sorted(pd.to_datetime(week_df["WeekStart"].dropna().unique()))

        if roadmap_weeks:
            week_options = {wk.strftime("%b %d, %Y"): wk for wk in roadmap_weeks}
            chosen_week_label = st.selectbox("Focus week", list(week_options.keys()), index=0)
            chosen_week = pd.Timestamp(week_options[chosen_week_label])

            for wk in roadmap_weeks:
                wk = pd.Timestamp(wk)
                wk_str = wk.strftime("%Y-%m-%d")
                wk_end = wk + pd.Timedelta(days=6)
                wk_tasks = week_df[(week_df["StartDate"] <= wk_end) & (week_df["EndDate"] >= wk)].copy()
                if wk_tasks.empty:
                    continue

                st.markdown(
                    f"""
                    <div class="roadmap-card">
                      <div class="roadmap-title">Week of {wk.strftime('%b %d, %Y')}</div>
                      <div class="roadmap-sub">{len(wk_tasks)} active task(s)</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_a, col_b, col_c = st.columns([1.1, 1.1, 2.4])

                by_proj = wk_tasks.groupby("Project").size().reset_index(name="Tasks")
                figp = px.bar(by_proj, x="Project", y="Tasks", text="Tasks", color="Project", color_discrete_map=PROJECT_COLORS, height=240)
                figp.update_layout(margin=dict(l=10, r=10, t=20, b=10), showlegend=False, xaxis_title="", yaxis_title="")
                figp.update_traces(textposition="outside")
                render_plotly(col_a, figp, f"roadmap_project_{wk_str}")

                by_stat = wk_tasks.groupby("Status").size().reset_index(name="Tasks")
                figs = px.bar(by_stat, x="Status", y="Tasks", text="Tasks", color="Status", color_discrete_map=STATUS_COLORS, height=240)
                figs.update_layout(margin=dict(l=10, r=10, t=20, b=10), showlegend=False, xaxis_title="", yaxis_title="")
                figs.update_traces(textposition="outside")
                render_plotly(col_b, figs, f"roadmap_status_{wk_str}")

                wk_show = wk_tasks[["Project", "Prototype", "Task", "Status", "Progress"]].sort_values(["Project", "Prototype", "Task"]).copy()
                wk_show["Progress"] = wk_show["Progress"].round(0).astype(int).astype(str) + "%"
                col_c.table(make_styled_table(wk_show, project_col="Project", font_size="10px"))

            st.markdown("### Focus week details")
            focus_start = chosen_week
            focus_end = focus_start + pd.Timedelta(days=6)
            focus_tasks = week_df[(week_df["StartDate"] <= focus_end) & (week_df["EndDate"] >= focus_start)].copy()
            focus_tasks["TaskLabel"] = focus_tasks.apply(lambda r: f"{r['Prototype']} • {r['Task']}", axis=1)

            if not focus_tasks.empty:
                fig_focus = px.bar(
                    focus_tasks.sort_values(["Project", "Prototype", "Task"]),
                    x="Progress",
                    y="TaskLabel",
                    orientation="h",
                    color="Status",
                    color_discrete_map=STATUS_COLORS,
                    title=f"Task progress for week of {focus_start.strftime('%b %d, %Y')}",
                    height=max(400, 28 * len(focus_tasks) + 120),
                )
                fig_focus.update_layout(xaxis_title="Progress (%)", yaxis_title="", legend_title_text="Status")
                render_plotly(st, fig_focus, f"focus_week_progress_{focus_start.strftime('%Y-%m-%d')}")

with tab3:
    st.subheader("Dashboard")
    if len(filtered):
        left, right = st.columns(2)

        by_status = filtered.groupby("Status", dropna=False).size().reset_index(name="Count")
        fig1 = px.bar(by_status, x="Status", y="Count", text="Count", color="Status", color_discrete_map=STATUS_COLORS, title="Tasks by status")
        fig1.update_layout(xaxis_title="", yaxis_title="Tasks")
        fig1.update_traces(textposition="outside")
        render_plotly(left, fig1, "dashboard_status")

        by_project = filtered.groupby("Project", dropna=False)["Progress"].mean().reset_index().sort_values("Progress", ascending=True)
        fig2 = px.bar(by_project, x="Progress", y="Project", orientation="h", text="Progress", color="Project", color_discrete_map=PROJECT_COLORS, title="Average progress by project")
        fig2.update_layout(yaxis_title="", xaxis_title="Average progress (%)", showlegend=False)
        fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        render_plotly(right, fig2, "dashboard_project_progress")

        a, b = st.columns(2)

        by_proto = filtered.groupby("Prototype", dropna=False)["Progress"].mean().reset_index().sort_values("Progress", ascending=True)
        fig3 = px.bar(by_proto, x="Progress", y="Prototype", orientation="h", text="Progress", color="Prototype", color_discrete_sequence=CHART_PALETTE, title="Average progress by prototype")
        fig3.update_layout(yaxis_title="", xaxis_title="Average progress (%)", showlegend=False)
        fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        render_plotly(a, fig3, "dashboard_prototype_progress")

        owner_load = filtered.explode("Owners")
        owner_load = owner_load[owner_load["Owners"].notna() & (owner_load["Owners"] != "")]
        owner_summary = owner_load.groupby("Owners").agg(Tasks=("Task", "count"), AvgProgress=("Progress", "mean")).reset_index().sort_values("Tasks", ascending=True)
        fig4 = px.bar(owner_summary, x="Tasks", y="Owners", orientation="h", text="Tasks", color="Owners", color_discrete_sequence=CHART_PALETTE, title="Task load by owner")
        fig4.update_layout(yaxis_title="", xaxis_title="Tasks", showlegend=False)
        fig4.update_traces(textposition="outside")
        render_plotly(b, fig4, "dashboard_owner_load")

        overdue_df = filtered[filtered["Overdue"]].copy()
        st.markdown("**Overdue tasks**")
        if overdue_df.empty:
            st.success("No overdue tasks in the current filtered view.")
        else:
            overdue_df["EndDate"] = pd.to_datetime(overdue_df["EndDate"], errors="coerce").dt.strftime("%b %d")
            overdue_df["Progress"] = overdue_df["Progress"].round(0).astype(int).astype(str) + "%"
            overdue_show = overdue_df[["Project", "Prototype", "Task", "OwnersLabel", "EndDate", "Status", "Progress"]]
            st.table(make_styled_table(overdue_show, project_col="Project", font_size="11px"))

with tab4:
    st.subheader("Tasks table")
    st.markdown('<div class="small-note">Clear table view of the filtered tasks. Use this as the operational list, then jump to the editor tab to update a specific task.</div>', unsafe_allow_html=True)

    show_cols = ["Project", "Prototype", "Stage", "Task", "OwnersLabel", "StartDate", "EndDate", "DurationDays", "Status", "Progress", "Priority", "WeeklyUpdate", "Notes", "LabRequired"]
    table_df = filtered[show_cols].copy().rename(columns={"OwnersLabel": "Owners"})
    table_df["StartDate"] = pd.to_datetime(table_df["StartDate"], errors="coerce").dt.strftime("%b %d")
    table_df["EndDate"] = pd.to_datetime(table_df["EndDate"], errors="coerce").dt.strftime("%b %d")
    table_df["Progress"] = table_df["Progress"].round(0).astype(int).astype(str) + "%"
    st.table(make_styled_table(table_df, project_col="Project", font_size="10px"))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Project slice**")
        project_focus = st.selectbox("View one project", ["All"] + project_options, index=0)
        if project_focus != "All":
            st.table(make_styled_table(table_df[table_df["Project"] == project_focus], project_col="Project", font_size="10px"))
    with c2:
        st.markdown("**Prototype slice**")
        prototype_focus = st.selectbox("View one prototype", ["All"] + prototype_options, index=0)
        if prototype_focus != "All":
            st.table(make_styled_table(table_df[table_df["Prototype"] == prototype_focus], project_col="Project", font_size="10px"))

with tab5:
    st.subheader("Task editor")
    st.markdown('<div class="small-note">Edit one task at a time here. This keeps the app stable while still giving you full control over owners, progress, dates, and notes.</div>', unsafe_allow_html=True)

    row_options = [f"{idx} | {row['Project']} | {row['Prototype']} | {row['Task']}" for idx, row in filtered.iterrows()]
    if row_options:
        selected_label = st.selectbox("Select task", row_options)
        selected_index = int(selected_label.split(" | ")[0])
        row = tasks.loc[selected_index].copy()

        c1, c2, c3 = st.columns(3)
        new_project = c1.selectbox("Project", project_options, index=project_options.index(row["Project"]) if row["Project"] in project_options else 0)
        new_prototype = c2.selectbox("Prototype", prototype_options, index=prototype_options.index(row["Prototype"]) if row["Prototype"] in prototype_options else 0)
        new_priority = c3.selectbox("Priority", PRIORITY_OPTIONS, index=PRIORITY_OPTIONS.index(row["Priority"]) if row["Priority"] in PRIORITY_OPTIONS else 1)

        d1, d2, d3 = st.columns(3)
        new_status = d1.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(row["Status"]) if row["Status"] in STATUS_OPTIONS else 0)
        new_progress = d2.slider("Progress (%)", 0, 100, int(row["Progress"]), 5)
        new_lab = d3.selectbox("Lab required", ["", "Yes"], index=1 if str(row["LabRequired"]) == "Yes" else 0)

        e1, e2 = st.columns(2)
        new_start = e1.date_input("Start date", value=row["StartDate"].date() if pd.notna(row["StartDate"]) else pd.Timestamp.today().date())
        new_end = e2.date_input("End date", value=row["EndDate"].date() if pd.notna(row["EndDate"]) else pd.Timestamp.today().date())

        new_stage = st.text_input("Stage / general activity", value=str(row["Stage"]))
        new_task = st.text_input("Task name", value=str(row["Task"]))
        new_owners = st.multiselect("Owners", people_options, default=[o for o in row["Owners"] if o in people_options])
        new_update = st.text_input("Weekly update", value=str(row["WeeklyUpdate"]))
        new_notes = st.text_area("Notes", value=str(row["Notes"]))

        if st.button("Save selected task"):
            tasks.loc[selected_index, "Project"] = new_project
            tasks.loc[selected_index, "Prototype"] = new_prototype
            tasks.loc[selected_index, "Priority"] = new_priority
            tasks.loc[selected_index, "Status"] = new_status
            tasks.loc[selected_index, "Progress"] = new_progress
            tasks.loc[selected_index, "LabRequired"] = new_lab
            tasks.loc[selected_index, "StartDate"] = pd.to_datetime(new_start)
            tasks.loc[selected_index, "EndDate"] = pd.to_datetime(new_end)
            tasks.loc[selected_index, "DurationDays"] = compute_duration_days(new_start, new_end)
            tasks.loc[selected_index, "Stage"] = new_stage
            tasks.loc[selected_index, "Task"] = new_task
            tasks.loc[selected_index, "Owners"] = new_owners
            tasks.loc[selected_index, "WeeklyUpdate"] = new_update
            tasks.loc[selected_index, "Notes"] = new_notes
            save_tasks(tasks)
            st.success("Task updated successfully.")

    st.markdown("### Add a manual mini-task")
    with st.form("manual_task_form_v9"):
        c1, c2, c3 = st.columns(3)
        project = c1.selectbox("Project", project_options)
        prototype = c2.selectbox("Prototype", prototype_options)
        priority = c3.selectbox("Priority", PRIORITY_OPTIONS, index=1)

        stage = st.text_input("Stage / general activity", value="General")
        task_name = st.text_input("Task name")
        owners = st.multiselect("Owners", people_options)
        d1, d2, d3 = st.columns(3)
        start = d1.date_input("Start date", key="manual_start_v9")
        end = d2.date_input("End date", key="manual_end_v9")
        status = d3.selectbox("Initial status", STATUS_OPTIONS)
        weekly_update = st.text_input("Weekly update")
        notes = st.text_area("Notes")
        lab_required = st.selectbox("Lab required?", ["", "Yes"])

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
            st.success("Manual task added.")

with tab6:
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
        week_tasks["Progress"] = week_tasks["Progress"].round(0).astype(int).astype(str) + "%"
        week_tasks["StartDate"] = pd.to_datetime(week_tasks["StartDate"], errors="coerce").dt.strftime("%b %d")
        week_tasks["EndDate"] = pd.to_datetime(week_tasks["EndDate"], errors="coerce").dt.strftime("%b %d")

        k1, k2, k3 = st.columns(3)
        k1.metric("Active tasks", int(len(week_tasks)))
        k2.metric("Completed", int((week_tasks["Status"] == "Done").sum()))
        k3.metric("Average progress", f"{round(report_df[(report_df['StartDate'] <= week_end) & (report_df['EndDate'] >= week_start)]['Progress'].mean() if len(week_tasks) else 0, 1)}%")

        week_show = week_tasks[["Project", "Prototype", "Task", "OwnersLabel", "StartDate", "EndDate", "Status", "Progress", "WeeklyUpdate", "Notes"]]
        st.table(make_styled_table(week_show, project_col="Project", font_size="10px"))
