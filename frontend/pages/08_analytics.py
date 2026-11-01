import streamlit as st
import requests
import plotly.graph_objects as go

BACKEND = "http://localhost:5000"
st.set_page_config(page_title="Analytics — TeamSync", page_icon="📊", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:linear-gradient(135deg,#0d1117,#161b22,#0d1117);color:#e6edf3;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#161b22,#0d1117);border-right:1px solid #30363d;}
.ts-card{background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem;}
.kpi-card{background:linear-gradient(135deg,rgba(22,27,34,.95),rgba(13,17,23,.95));border:1px solid #30363d;
  border-radius:14px;padding:1.2rem;text-align:center;transition:transform .2s;}
.kpi-card:hover{transform:translateY(-2px);}
.formula-box{background:rgba(31,111,235,.05);border:1px solid rgba(31,111,235,.3);border-radius:10px;
  padding:1rem 1.5rem;margin:.8rem 0;font-family:monospace;}
</style>""", unsafe_allow_html=True)


def api_get(p, params=None):
    try: return requests.get(f"{BACKEND}{p}", params=params, timeout=8).json()
    except: return None


st.markdown("""
<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid #21262d;margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#e6edf3;">📊 Analytics & Reports</div>
  <div style="font-size:.9rem;color:#8b949e;">Project health · Productivity metrics · Progress trends</div>
</div>
""", unsafe_allow_html=True)

# Load data
overview = api_get("/api/analytics/overview", {"project_id": 1})
weekly = api_get("/api/analytics/weekly", {"project_id": 1, "weeks": 8})
workload = api_get("/api/analytics/workload", {"project_id": 1})

if not overview:
    st.warning("⚠️ Backend offline.")
    st.stop()

tasks = overview.get("tasks", {})
issues = overview.get("issues", {})
prs = overview.get("pull_requests", {})
health = overview.get("health_score", 0)
comp = overview.get("completion_rate", 0)
bug_rate = overview.get("bug_resolution_rate", 0)
ci_rate = overview.get("ci_success_rate", 0)

# ─── Health Score Breakdown ───────────────────────────────────────────────────
st.markdown("#### 🏥 Project Health Score")
st.markdown("""
<div class="formula-box">
    <div style="font-size:.82rem;color:#8b949e;margin-bottom:.5rem;">📐 Health Formula: H = 0.4×T + 0.3×M + 0.2×B + 0.1×C</div>
    <div style="font-size:.82rem;color:#8b949e;">T=Task Completion · M=Milestone Progress · B=Bug Resolution · C=CI Success Rate</div>
</div>
""", unsafe_allow_html=True)

ms_data = api_get("/api/github/milestones", {"project_id": 1})
ms_completion = 0
if ms_data:
    total_closed = sum(m.get("closed_issues",0) for m in ms_data)
    total_all = sum(m.get("open_issues",0)+m.get("closed_issues",0) for m in ms_data)
    ms_completion = round(total_closed/total_all*100, 1) if total_all > 0 else 0

col_h, col_comp = st.columns([1.5, 2.5])
with col_h:
    color = "#3fb950" if health >= 75 else "#e3b341" if health >= 50 else "#f85149"
    label = "Excellent" if health >= 75 else "Needs Attention" if health >= 50 else "Critical"
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=health,
        number={"suffix":"/100","font":{"size":32,"color":"#e6edf3","family":"Inter"}},
        gauge={
            "axis":{"range":[0,100],"tickcolor":"#8b949e"},
            "bar":{"color":color},
            "bgcolor":"#21262d","bordercolor":"#30363d",
            "steps":[{"range":[0,50],"color":"rgba(218,54,51,.08)"},
                     {"range":[50,75],"color":"rgba(210,153,34,.08)"},
                     {"range":[75,100],"color":"rgba(35,134,54,.08)"}],
        },
    ))
    fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)",height=220,
                            margin=dict(l=20,r=20,t=20,b=20),font_color="#e6edf3")
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_comp:
    components = [
        ("Task Completion (40%)", comp, 40, "#58a6ff"),
        ("Milestone Progress (30%)", ms_completion, 30, "#bc6aff"),
        ("Bug Resolution (20%)", bug_rate, 20, "#3fb950"),
        ("CI Success Rate (10%)", ci_rate, 10, "#e3b341"),
    ]
    st.markdown("<br>", unsafe_allow_html=True)
    for lbl, val, weight, color in components:
        contribution = round(val * weight / 100, 1)
        st.markdown(f"""
        <div style="margin-bottom:.8rem;">
            <div style="display:flex;justify-content:space-between;font-size:.82rem;margin-bottom:.25rem;">
                <span style="color:#e6edf3;font-weight:500;">{lbl}</span>
                <span style="color:{color};font-weight:700;">{val}% → +{contribution} pts</span>
            </div>
            <div style="background:#21262d;border-radius:4px;height:8px;">
                <div style="width:{min(val,100)}%;height:100%;background:{color};border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ─── KPI Grid ────────────────────────────────────────────────────────────────
st.markdown("#### 📐 Key Metrics")
kpi_cols = st.columns(4)
kpis = [
    ("Task Completion Rate", f"{comp}%", f"Task Completion = {tasks.get('completed',0)}/{tasks.get('total',0)} × 100", "#58a6ff"),
    ("Bug Resolution Rate", f"{bug_rate}%", f"Bug Resolution = {issues.get('bugs_total',0)-issues.get('bugs_open',0)}/{issues.get('bugs_total',0)} × 100", "#3fb950"),
    ("PR Merge Rate", f"{prs.get('merge_rate',0)}%", f"PR Merge = {prs.get('merged',0)}/{prs.get('total',0)} × 100", "#bc6aff"),
    ("CI Success Rate", f"{ci_rate}%", "Based on GitHub Actions check results", "#e3b341"),
]
for col, (lbl, val, formula, color) in zip(kpi_cols, kpis):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size:1.8rem;font-weight:800;color:{color};">{val}</div>
            <div style="font-size:.78rem;font-weight:600;color:#e6edf3;margin:.2rem 0;">{lbl}</div>
            <div style="font-size:.7rem;color:#8b949e;">{formula}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Weekly Trend ─────────────────────────────────────────────────────────────
col_week, col_status = st.columns([2, 1.5])

with col_week:
    st.markdown('<div class="ts-card">', unsafe_allow_html=True)
    st.markdown("#### 📈 Weekly Task Completion Trend")
    if weekly:
        fig_week = go.Figure()
        fig_week.add_trace(go.Scatter(
            x=[d["label"] for d in weekly],
            y=[d["completed"] for d in weekly],
            mode="lines+markers+text",
            line=dict(color="#58a6ff", width=2.5, shape="spline"),
            marker=dict(size=8, color="#58a6ff", line=dict(color="#0d1117", width=2)),
            text=[d["completed"] for d in weekly],
            textposition="top center",
            textfont=dict(color="#8b949e", size=10),
            fill="tozeroy",
            fillcolor="rgba(88,166,255,0.08)",
        ))
        fig_week.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=230, font_color="#e6edf3", margin=dict(l=10,r=10,t=10,b=10),
            xaxis=dict(showgrid=False, color="#8b949e"),
            yaxis=dict(showgrid=True, gridcolor="#21262d", color="#8b949e"),
        )
        st.plotly_chart(fig_week, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_status:
    st.markdown('<div class="ts-card">', unsafe_allow_html=True)
    st.markdown("#### 🟠 Task Status")
    t_labels = ["Completed","In Progress","In Review","To Do","Blocked"]
    t_values = [tasks.get("completed",0),tasks.get("in_progress",0),
                tasks.get("in_review",0),tasks.get("todo",0),tasks.get("blocked",0)]
    t_colors = ["#3fb950","#58a6ff","#bc6aff","#8b949e","#f85149"]
    if sum(t_values) > 0:
        fig_pie = go.Figure(go.Pie(
            labels=t_labels, values=t_values, hole=0.6,
            marker=dict(colors=t_colors, line=dict(color="#0d1117",width=2)),
            textinfo="percent", textfont_size=10,
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", height=230,
            margin=dict(l=0,r=0,t=0,b=0),font_color="#e6edf3",
            legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=10,color="#8b949e")),
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Developer Productivity Table ────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 👥 Developer Productivity Summary")
if workload:
    import pandas as pd
    df = pd.DataFrame([{
        "Developer": w["name"],
        "Role": w.get("role","developer"),
        "Total Tasks": w["total_tasks"],
        "✅ Completed": w["completed"],
        "🔄 In Progress": w["in_progress"],
        "⚠️ Overdue": w["overdue"],
        "📈 Completion Rate": f'{w["completion_rate"]}%',
    } for w in workload])
    st.dataframe(df, use_container_width=True, hide_index=True)
