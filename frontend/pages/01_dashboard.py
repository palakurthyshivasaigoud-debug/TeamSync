import streamlit as st
import requests
import plotly.graph_objects as go
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BACKEND = "http://localhost:5000"

st.set_page_config(page_title="Dashboard — TeamSync", page_icon="🏠", layout="wide")

# ─── Shared CSS ───────────────────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg,#0d1117 0%,#161b22 50%,#0d1117 100%); color: #e6edf3; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#161b22,#0d1117); border-right:1px solid #30363d; }
.metric-card { background:linear-gradient(135deg,rgba(22,27,34,.95),rgba(13,17,23,.95)); border:1px solid #30363d;
  border-radius:14px; padding:1.4rem; text-align:center; transition:transform .2s,box-shadow .2s; }
.metric-card:hover { transform:translateY(-3px); box-shadow:0 8px 32px rgba(88,166,255,.15); }
.metric-value { font-size:2.4rem; font-weight:800; line-height:1; margin-bottom:.3rem; }
.metric-label { font-size:.78rem; font-weight:500; color:#8b949e; text-transform:uppercase; letter-spacing:.08em; }
.ts-card { background:rgba(22,27,34,.9); border:1px solid #30363d; border-radius:12px; padding:1.2rem 1.5rem;
  margin-bottom:1rem; transition:all .2s; }
.ts-card:hover { border-color:#58a6ff; box-shadow:0 4px 24px rgba(88,166,255,.1); }
.badge { display:inline-block; padding:.2rem .6rem; border-radius:20px; font-size:.72rem; font-weight:600;
  letter-spacing:.04em; text-transform:uppercase; }
.badge-green { background:rgba(35,134,54,.2); color:#3fb950; border:1px solid #238636; }
.badge-red { background:rgba(218,54,51,.2); color:#f85149; border:1px solid #da3633; }
.badge-yellow { background:rgba(210,153,34,.2); color:#e3b341; border:1px solid #d29922; }
.badge-blue { background:rgba(31,111,235,.2); color:#58a6ff; border:1px solid #1f6feb; }
.badge-gray { background:rgba(110,118,129,.2); color:#8b949e; border:1px solid #6e7681; }
.page-title { font-size:1.8rem; font-weight:700; color:#e6edf3; }
.page-subtitle { font-size:.9rem; color:#8b949e; margin-top:.3rem; }
.stButton>button { background:linear-gradient(135deg,#1f6feb,#388bfd); color:white; border:none;
  border-radius:8px; font-weight:600; transition:all .2s; }
</style>""", unsafe_allow_html=True)


def api(path, params=None):
    try:
        return requests.get(f"{BACKEND}{path}", params=params, timeout=8).json()
    except:
        return None


def health_gauge(score):
    color = "#3fb950" if score >= 75 else "#e3b341" if score >= 50 else "#f85149"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        number={"suffix": "/100", "font": {"size": 36, "color": "#e6edf3", "family": "Inter"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#8b949e", "tickfont": {"color": "#8b949e"}},
            "bar": {"color": color},
            "bgcolor": "#21262d",
            "bordercolor": "#30363d",
            "steps": [
                {"range": [0, 50], "color": "rgba(218,54,51,0.1)"},
                {"range": [50, 75], "color": "rgba(210,153,34,0.1)"},
                {"range": [75, 100], "color": "rgba(35,134,54,0.1)"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": score},
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3", height=220, margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def donut_chart(labels, values, colors):
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color="#0d1117", width=2)),
        textfont_size=11,
        textinfo="percent",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3", height=200,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(font=dict(size=10, color="#8b949e"), bgcolor="rgba(0,0,0,0)"),
        showlegend=True,
    )
    return fig


def weekly_bar(data):
    fig = go.Figure(go.Bar(
        x=[d["label"] for d in data],
        y=[d["completed"] for d in data],
        marker=dict(
            color=[d["completed"] for d in data],
            colorscale=[[0, "#1f6feb"], [1, "#58a6ff"]],
            showscale=False,
            line=dict(width=0),
        ),
        text=[d["completed"] for d in data],
        textposition="outside",
        textfont=dict(color="#8b949e", size=10),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3", height=180,
        xaxis=dict(showgrid=False, color="#8b949e"),
        yaxis=dict(showgrid=True, gridcolor="#21262d", color="#8b949e"),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig


# ─── Main Dashboard ──────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1rem 0 1.5rem 0; border-bottom:1px solid #21262d; margin-bottom:1.5rem;">
  <div class="page-title">🏠 Project Dashboard</div>
  <div class="page-subtitle">Online Examination System — Real-time project health overview</div>
</div>
""", unsafe_allow_html=True)

# Fetch data
overview = api("/api/analytics/overview", {"project_id": 1})
weekly = api("/api/analytics/weekly", {"project_id": 1, "weeks": 8})
workload = api("/api/analytics/workload", {"project_id": 1})

if not overview:
    st.warning("⚠️ Cannot reach backend. Start the Flask server: `python run_backend.py`")
    st.stop()

tasks = overview.get("tasks", {})
issues = overview.get("issues", {})
prs = overview.get("pull_requests", {})
ms = overview.get("milestones", {})
health_score = overview.get("health_score", 0)
completion = overview.get("completion_rate", 0)
days_left = overview.get("days_remaining")

# ─── Top KPI Row ─────────────────────────────────────────────────────────────
cols = st.columns(6)
kpis = [
    ("🎯", f"{completion}%", "Completion", "#58a6ff"),
    ("✅", tasks.get("completed", 0), "Tasks Done", "#3fb950"),
    ("🔄", tasks.get("in_progress", 0), "In Progress", "#e3b341"),
    ("🔀", prs.get("open", 0), "Open PRs", "#bc6aff"),
    ("🐛", issues.get("bugs_open", 0), "Open Bugs", "#f85149"),
    ("📅", f"{days_left}d" if days_left is not None else "—", "Days Left", "#e3b341" if days_left and days_left < 7 else "#58a6ff"),
]
for col, (icon, value, label, color) in zip(cols, kpis):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.6rem;">{icon}</div>
            <div class="metric-value" style="color:{color};">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Row 2: Health + Task Distribution + Weekly ───────────────────────────────
col_health, col_donut, col_weekly = st.columns([1.2, 1.5, 2])

with col_health:
    st.markdown('<div class="ts-card">', unsafe_allow_html=True)
    st.markdown("#### 🏥 Project Health")
    st.plotly_chart(health_gauge(health_score), use_container_width=True)
    hcolor = "#3fb950" if health_score >= 75 else "#e3b341" if health_score >= 50 else "#f85149"
    hlabel = "Excellent" if health_score >= 75 else "Needs Attention" if health_score >= 50 else "Critical"
    st.markdown(f'<div style="text-align:center;"><span class="badge" style="background:rgba(88,166,255,.1);color:{hcolor};border-color:{hcolor};">{hlabel}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_donut:
    st.markdown('<div class="ts-card">', unsafe_allow_html=True)
    st.markdown("#### 📋 Task Status")
    t_labels = ["Completed", "In Progress", "In Review", "To Do", "Blocked"]
    t_values = [
        tasks.get("completed", 0), tasks.get("in_progress", 0),
        tasks.get("in_review", 0), tasks.get("todo", 0), tasks.get("blocked", 0),
    ]
    t_colors = ["#3fb950", "#58a6ff", "#bc6aff", "#8b949e", "#f85149"]
    if sum(t_values) > 0:
        st.plotly_chart(donut_chart(t_labels, t_values, t_colors), use_container_width=True)
    else:
        st.info("No tasks found")
    st.markdown("</div>", unsafe_allow_html=True)

with col_weekly:
    st.markdown('<div class="ts-card">', unsafe_allow_html=True)
    st.markdown("#### 📈 Weekly Task Completions")
    if weekly:
        st.plotly_chart(weekly_bar(weekly), use_container_width=True)
    else:
        st.info("No weekly data available")
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Row 3: Overdue Tasks + PR Status + Workload ─────────────────────────────
col_overdue, col_prs, col_wload = st.columns([1.5, 1.5, 2])

with col_overdue:
    st.markdown('<div class="ts-card">', unsafe_allow_html=True)
    st.markdown("#### ⚠️ Overdue Tasks")
    overdue_count = tasks.get("overdue", 0)
    blocked_count = tasks.get("blocked", 0)
    if overdue_count == 0 and blocked_count == 0:
        st.markdown('<div class="success-block">✅ No overdue or blocked tasks!</div>', unsafe_allow_html=True)
    else:
        if overdue_count > 0:
            st.markdown(f'<div class="error-block">🔴 {overdue_count} task(s) past deadline</div>', unsafe_allow_html=True)
        if blocked_count > 0:
            st.markdown(f'<div class="warning-block">🟡 {blocked_count} task(s) blocked</div>', unsafe_allow_html=True)

    st.markdown("##### PR Checks")
    failed_prs = prs.get("failed_checks", 0)
    pending_review = prs.get("pending_review", 0)
    if failed_prs > 0:
        st.markdown(f'<div class="error-block">❌ {failed_prs} PR(s) failing CI checks</div>', unsafe_allow_html=True)
    if pending_review > 0:
        st.markdown(f'<div class="warning-block">👁 {pending_review} PR(s) awaiting review</div>', unsafe_allow_html=True)
    if failed_prs == 0 and pending_review == 0:
        st.markdown('<div class="success-block">✅ All PRs healthy</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_prs:
    st.markdown('<div class="ts-card">', unsafe_allow_html=True)
    st.markdown("#### 🔀 Pull Request Summary")

    pr_labels = ["Open", "Merged"]
    pr_values = [prs.get("open", 0), prs.get("merged", 0)]
    pr_colors = ["#58a6ff", "#3fb950"]

    if sum(pr_values) > 0:
        fig2 = donut_chart(pr_labels, pr_values, pr_colors)
        st.plotly_chart(fig2, use_container_width=True)

    merge_rate = prs.get("merge_rate", 0)
    st.markdown(f"""
    <div style="display:flex;justify-content:space-around;font-size:0.8rem;margin-top:0.5rem;">
        <div style="text-align:center;"><span style="color:#58a6ff;font-weight:700;">{prs.get('open',0)}</span><br><span style="color:#8b949e;">Open</span></div>
        <div style="text-align:center;"><span style="color:#3fb950;font-weight:700;">{prs.get('merged',0)}</span><br><span style="color:#8b949e;">Merged</span></div>
        <div style="text-align:center;"><span style="color:#e3b341;font-weight:700;">{merge_rate}%</span><br><span style="color:#8b949e;">Merge Rate</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_wload:
    st.markdown('<div class="ts-card">', unsafe_allow_html=True)
    st.markdown("#### 👥 Developer Workload")
    if workload:
        names = [w["name"].split()[0] for w in workload]
        totals = [w["total_tasks"] for w in workload]
        completed_wl = [w["completed"] for w in workload]

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name="Completed", x=names, y=completed_wl,
            marker_color="#3fb950", text=completed_wl, textposition="inside",
        ))
        fig3.add_trace(go.Bar(
            name="In Progress", x=names, y=[t - c for t, c in zip(totals, completed_wl)],
            marker_color="#58a6ff",
        ))
        fig3.update_layout(
            barmode="stack", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e6edf3", height=190, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False, color="#8b949e"),
            yaxis=dict(showgrid=True, gridcolor="#21262d", color="#8b949e"),
            legend=dict(font=dict(size=10, color="#8b949e"), bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Row 4: Milestone Progress ────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 🏁 Milestone Progress")

milestones_data = api("/api/github/milestones", {"project_id": 1})
if milestones_data:
    cols_ms = st.columns(len(milestones_data))
    for col, ms_item in zip(cols_ms, milestones_data):
        prog = ms_item.get("progress", 0)
        color = "#3fb950" if prog == 100 else "#58a6ff" if prog > 50 else "#e3b341"
        status_badge = "badge-green" if ms_item["status"] == "closed" else "badge-blue"
        with col:
            st.markdown(f"""
            <div class="ts-card">
                <div style="font-weight:600;font-size:0.85rem;margin-bottom:0.4rem;">{ms_item['title']}</div>
                <span class="badge {status_badge}">{ms_item['status']}</span>
                <div style="margin-top:0.8rem;">
                    <div style="font-size:1.4rem;font-weight:700;color:{color};">{prog}%</div>
                    <div style="background:#21262d;border-radius:4px;height:6px;margin-top:0.4rem;">
                        <div style="width:{prog}%;height:100%;background:{color};border-radius:4px;"></div>
                    </div>
                </div>
                <div style="font-size:0.72rem;color:#8b949e;margin-top:0.4rem;">
                    {ms_item.get('closed_issues',0)} / {ms_item.get('open_issues',0)+ms_item.get('closed_issues',0)} issues
                </div>
            </div>
            """, unsafe_allow_html=True)
