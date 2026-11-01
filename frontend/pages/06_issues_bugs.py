import streamlit as st
import requests

BACKEND = "http://localhost:5000"
st.set_page_config(page_title="Issues & Bugs — TeamSync", page_icon="🐛", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:linear-gradient(135deg,#0d1117,#161b22,#0d1117);color:#e6edf3;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#161b22,#0d1117);border-right:1px solid #30363d;}
.issue-card{background:rgba(22,27,34,.9);border-left:3px solid #30363d;border-radius:0 10px 10px 0;
  padding:1rem 1.3rem;margin-bottom:.6rem;transition:all .2s;border-top:1px solid #30363d;
  border-right:1px solid #30363d;border-bottom:1px solid #30363d;}
.issue-card.bug{border-left-color:#da3633;}
.issue-card.open{border-left-color:#238636;}
.issue-card.closed{border-left-color:#6e7681;}
.badge{display:inline-block;padding:.2rem .6rem;border-radius:20px;font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:.04em;}
.badge-green{background:rgba(35,134,54,.2);color:#3fb950;border:1px solid #238636;}
.badge-red{background:rgba(218,54,51,.2);color:#f85149;border:1px solid #da3633;}
.badge-yellow{background:rgba(210,153,34,.2);color:#e3b341;border:1px solid #d29922;}
.badge-blue{background:rgba(31,111,235,.2);color:#58a6ff;border:1px solid #1f6feb;}
.badge-gray{background:rgba(110,118,129,.2);color:#8b949e;border:1px solid #6e7681;}
.label-chip{display:inline-block;background:rgba(88,166,255,.1);color:#58a6ff;
  border:1px solid rgba(88,166,255,.3);border-radius:12px;padding:.1rem .5rem;
  font-size:.7rem;margin:.1rem;}
.metric-box{background:rgba(13,17,23,.8);border:1px solid #30363d;border-radius:10px;padding:1rem;text-align:center;}
.stButton>button{background:linear-gradient(135deg,#1f6feb,#388bfd);color:white;border:none;border-radius:8px;font-weight:600;}
</style>""", unsafe_allow_html=True)


def api_get(p, params=None):
    try: return requests.get(f"{BACKEND}{p}", params=params, timeout=8).json()
    except: return []

def api_post(p, data):
    try: return requests.post(f"{BACKEND}{p}", json=data, timeout=8).json()
    except: return None


st.markdown("""
<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid #21262d;margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#e6edf3;">🐛 Issues & Bug Tracking</div>
  <div style="font-size:.9rem;color:#8b949e;">GitHub Issues synchronized · Bug classification · Resolution monitoring</div>
</div>
""", unsafe_allow_html=True)

tab_issues, tab_bugs, tab_new = st.tabs(["📋 All Issues", "🔴 Bug Tracker", "➕ Create Issue"])

with tab_issues:
    issues = api_get("/api/github/issues", {"project_id": 1})
    if not issues:
        st.warning("No issues found. Start backend.")
        st.stop()

    open_issues = [i for i in issues if i["state"] == "open"]
    closed_issues = [i for i in issues if i["state"] == "closed"]
    all_bugs = [i for i in issues if i.get("is_bug")]

    # Metrics
    cols = st.columns(4)
    for col, (icon, val, lbl, color) in zip(cols, [
        ("📋", len(issues), "Total Issues", "#58a6ff"),
        ("🟢", len(open_issues), "Open", "#3fb950"),
        ("✅", len(closed_issues), "Closed", "#8b949e"),
        ("🔴", len([b for b in all_bugs if b["state"]=="open"]), "Open Bugs", "#f85149"),
    ]):
        with col:
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size:1.4rem;">{icon}</div>
                <div style="font-size:2rem;font-weight:800;color:{color};">{val}</div>
                <div style="font-size:.73rem;color:#8b949e;text-transform:uppercase;">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filters
    c1, c2 = st.columns(2)
    with c1: state_f = st.radio("State", ["All","Open","Closed"], horizontal=True)
    with c2: bug_only = st.checkbox("🔴 Bugs only")

    filtered = issues
    if state_f == "Open": filtered = open_issues
    elif state_f == "Closed": filtered = closed_issues
    if bug_only: filtered = [i for i in filtered if i.get("is_bug")]

    st.markdown(f"**{len(filtered)} issues**")

    for issue in filtered:
        is_bug = issue.get("is_bug", False)
        is_open = issue.get("state") == "open"
        card_class = "bug" if is_bug else "open" if is_open else "closed"

        labels = issue.get("labels", [])
        if isinstance(labels, str): labels = labels.split(",") if labels else []
        labels_html = "".join(f'<span class="label-chip">{l.strip()}</span>' for l in labels if l.strip())
        state_badge = "badge-green" if is_open else "badge-gray"
        bug_badge = '<span class="badge badge-red">🔴 BUG</span>' if is_bug else ""
        gh_url = issue.get("github_url", "#")

        st.markdown(f"""
        <div class="issue-card {card_class}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div style="flex:1;">
                    <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.3rem;">
                        <span style="color:#8b949e;font-size:.8rem;">#{issue.get('github_issue_number','?')}</span>
                        <a href="{gh_url}" target="_blank"
                           style="font-weight:600;font-size:.92rem;color:#e6edf3;text-decoration:none;">
                            {issue.get('title','')}
                        </a>
                    </div>
                    <div style="margin:.3rem 0;">{labels_html}</div>
                    <div style="font-size:.78rem;color:#8b949e;">
                        👤 {issue.get('author','?')} &nbsp;·&nbsp;
                        Assigned: {issue.get('assignee','Unassigned') or 'Unassigned'}
                        {f'&nbsp;·&nbsp; 🏁 {issue.get("milestone","")}' if issue.get("milestone") else ''}
                    </div>
                </div>
                <div style="display:flex;flex-direction:column;gap:.3rem;align-items:flex-end;">
                    <span class="badge {state_badge}">{'🟢 Open' if is_open else '✅ Closed'}</span>
                    {bug_badge}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab_bugs:
    issues = api_get("/api/github/issues", {"project_id": 1})
    bugs = [i for i in (issues or []) if i.get("is_bug")]
    open_bugs = [b for b in bugs if b["state"] == "open"]
    closed_bugs = [b for b in bugs if b["state"] == "closed"]

    resolution_rate = round(len(closed_bugs) / len(bugs) * 100, 1) if bugs else 0

    st.markdown(f"""
    <div style="display:flex;gap:1rem;margin-bottom:1.5rem;">
        <div class="metric-box" style="flex:1;"><div style="font-size:1.6rem;">🐛</div>
            <div style="font-size:2rem;font-weight:800;color:#f85149;">{len(bugs)}</div>
            <div style="font-size:.73rem;color:#8b949e;">TOTAL BUGS</div></div>
        <div class="metric-box" style="flex:1;"><div style="font-size:1.6rem;">🔴</div>
            <div style="font-size:2rem;font-weight:800;color:#f85149;">{len(open_bugs)}</div>
            <div style="font-size:.73rem;color:#8b949e;">OPEN</div></div>
        <div class="metric-box" style="flex:1;"><div style="font-size:1.6rem;">✅</div>
            <div style="font-size:2rem;font-weight:800;color:#3fb950;">{len(closed_bugs)}</div>
            <div style="font-size:.73rem;color:#8b949e;">RESOLVED</div></div>
        <div class="metric-box" style="flex:1;"><div style="font-size:1.6rem;">📈</div>
            <div style="font-size:2rem;font-weight:800;color:#58a6ff;">{resolution_rate}%</div>
            <div style="font-size:.73rem;color:#8b949e;">RESOLUTION RATE</div></div>
    </div>
    """, unsafe_allow_html=True)

    if open_bugs:
        st.markdown("#### 🔴 Open Bugs — Needs Attention")
        for bug in open_bugs:
            gh_url = bug.get("github_url","#")
            labels = bug.get("labels",[])
            if isinstance(labels,str): labels = labels.split(",") if labels else []
            labels_html = "".join(f'<span class="label-chip">{l.strip()}</span>' for l in labels if l.strip())
            st.markdown(f"""
            <div class="issue-card bug">
                <div style="display:flex;justify-content:space-between;">
                    <div>
                        <span style="color:#8b949e;font-size:.8rem;">#{bug.get('github_issue_number','?')}</span>&nbsp;
                        <a href="{gh_url}" target="_blank" style="font-weight:600;color:#f85149;text-decoration:none;">
                            {bug.get('title','')}
                        </a>
                        <div style="margin:.3rem 0;">{labels_html}</div>
                        <div style="font-size:.78rem;color:#8b949e;">
                            Assigned: {bug.get('assignee','Unassigned') or 'Unassigned'}
                        </div>
                    </div>
                    <span class="badge badge-red">🔴 Open</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab_new:
    st.markdown("#### ➕ Create New GitHub Issue")
    with st.form("new_issue_form"):
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("Issue Title *", placeholder="e.g., Login button not responding")
            body = st.text_area("Description", placeholder="Steps to reproduce, expected vs actual behavior...")
            labels = st.text_input("Labels (comma-separated)", placeholder="bug, authentication, high-priority")
        with c2:
            repo_owner = st.text_input("Repository Owner", value="teamsync-demo")
            repo_name = st.text_input("Repository Name", value="online-exam-system")
            assignees = st.text_input("Assignees (GitHub usernames, comma-separated)")

        if st.form_submit_button("🚀 Create Issue on GitHub", use_container_width=True):
            if not title:
                st.error("Title required!")
            else:
                st.info("💡 This would call `POST /repos/{owner}/{repo}/issues` on GitHub REST API with your token.")
                st.success(f"✅ Demo: Issue '{title}' would be created on GitHub!")
                st.code(f"""POST https://api.github.com/repos/{repo_owner}/{repo_name}/issues
Authorization: token YOUR_GITHUB_TOKEN
Content-Type: application/json

{{
  "title": "{title}",
  "body": "{body[:60]}...",
  "labels": {labels.split(',') if labels else []},
  "assignees": {[a.strip() for a in assignees.split(',')] if assignees else []}
}}""", language="http")
