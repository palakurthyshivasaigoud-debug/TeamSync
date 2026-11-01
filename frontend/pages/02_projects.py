import streamlit as st
import requests

BACKEND = "http://localhost:5000"
st.set_page_config(page_title="Projects — TeamSync", page_icon="📁", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:linear-gradient(135deg,#0d1117,#161b22,#0d1117);color:#e6edf3;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#161b22,#0d1117);border-right:1px solid #30363d;}
.proj-card{background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:14px;padding:1.5rem;
  margin-bottom:1rem;transition:all .2s;}
.proj-card:hover{border-color:#58a6ff;box-shadow:0 4px 24px rgba(88,166,255,.1);transform:translateY(-2px);}
.badge{display:inline-block;padding:.2rem .6rem;border-radius:20px;font-size:.72rem;font-weight:600;
  text-transform:uppercase;letter-spacing:.04em;}
.badge-green{background:rgba(35,134,54,.2);color:#3fb950;border:1px solid #238636;}
.badge-yellow{background:rgba(210,153,34,.2);color:#e3b341;border:1px solid #d29922;}
.badge-blue{background:rgba(31,111,235,.2);color:#58a6ff;border:1px solid #1f6feb;}
.badge-gray{background:rgba(110,118,129,.2);color:#8b949e;border:1px solid #6e7681;}
.stButton>button{background:linear-gradient(135deg,#1f6feb,#388bfd);color:white;border:none;
  border-radius:8px;font-weight:600;transition:all .2s;}
</style>""", unsafe_allow_html=True)


def api_get(p, params=None):
    try: return requests.get(f"{BACKEND}{p}", params=params, timeout=8).json()
    except: return None

def api_post(p, data):
    try: return requests.post(f"{BACKEND}{p}", json=data, timeout=8).json()
    except: return None


STATUS_BADGE = {"active":"badge-green","completed":"badge-green","on-hold":"badge-yellow","archived":"badge-gray"}

st.markdown("""
<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid #21262d;margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#e6edf3;">📁 Projects</div>
  <div style="font-size:.9rem;color:#8b949e;">Manage your GitHub-connected software projects</div>
</div>
""", unsafe_allow_html=True)

tab_list, tab_new = st.tabs(["📋 All Projects", "➕ New Project"])

with tab_list:
    projects = api_get("/api/projects/")
    if not projects:
        st.warning("⚠️ Backend offline.")
        st.stop()

    for proj in projects:
        comp = proj.get("completion_rate", 0)
        color = "#3fb950" if comp >= 75 else "#58a6ff" if comp >= 40 else "#e3b341"
        s_badge = STATUS_BADGE.get(proj.get("status","active"), "badge-gray")

        with st.container():
            st.markdown(f"""
            <div class="proj-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
                    <div>
                        <div style="font-size:1.25rem;font-weight:700;color:#e6edf3;">{proj['name']}</div>
                        <div style="font-size:.82rem;color:#8b949e;margin-top:.25rem;">{proj.get('description','')[:100]}...</div>
                    </div>
                    <div style="text-align:right;">
                        <span class="badge {s_badge}">{proj.get('status','active')}</span>
                        {f'<div style="font-size:.75rem;color:#8b949e;margin-top:.3rem;">📅 Deadline: {proj.get("deadline","—")}</div>' if proj.get("deadline") else ''}
                    </div>
                </div>
                <div style="display:flex;gap:2rem;margin-bottom:.8rem;">
                    <div style="text-align:center;">
                        <div style="font-size:1.5rem;font-weight:700;color:{color};">{comp}%</div>
                        <div style="font-size:.72rem;color:#8b949e;">Complete</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:1.5rem;font-weight:700;color:#e6edf3;">{proj.get('total_tasks',0)}</div>
                        <div style="font-size:.72rem;color:#8b949e;">Total Tasks</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:1.5rem;font-weight:700;color:#3fb950;">{proj.get('completed_tasks',0)}</div>
                        <div style="font-size:.72rem;color:#8b949e;">Completed</div>
                    </div>
                    <div style="flex:1;">
                        {f'<div style="font-size:.8rem;color:#8b949e;"><span style="color:#e6edf3;">🐙</span> <a href="https://github.com/{proj.get("github_repo","")}" target="_blank" style="color:#58a6ff;text-decoration:none;">{proj.get("github_repo","Not connected")}</a></div>' if proj.get("github_repo") else '<div style="font-size:.8rem;color:#8b949e;">🐙 No repository connected</div>'}
                        <div style="font-size:.78rem;color:#8b949e;margin-top:.2rem;">🛠 {proj.get("tech_stack","")}</div>
                    </div>
                </div>
                <div style="background:#21262d;border-radius:6px;height:6px;">
                    <div style="width:{comp}%;height:100%;background:linear-gradient(90deg,{color},{color}cc);border-radius:6px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab_new:
    st.markdown("#### ➕ Create New Project")
    with st.form("new_proj"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Project Name *", placeholder="e.g., E-Commerce Platform")
            description = st.text_area("Description", placeholder="Project description...")
            tech_stack = st.text_input("Tech Stack", placeholder="Python, Flask, React, PostgreSQL")
        with c2:
            repo_owner = st.text_input("GitHub Owner", placeholder="your-github-username")
            repo_name = st.text_input("Repository Name", placeholder="my-project-repo")
            start_date = st.date_input("Start Date")
            from datetime import date, timedelta
            deadline = st.date_input("Deadline", value=date.today() + timedelta(days=45))
            status = st.selectbox("Status", ["active","on-hold"])

        if st.form_submit_button("🚀 Create Project", use_container_width=True):
            if not name:
                st.error("Project name required!")
            else:
                result = api_post("/api/projects/", {
                    "name": name, "description": description,
                    "repository_owner": repo_owner or None,
                    "repository_name": repo_name or None,
                    "tech_stack": tech_stack,
                    "start_date": start_date.isoformat(),
                    "deadline": deadline.isoformat(),
                    "status": status, "owner_id": 1,
                })
                if result and "id" in result:
                    st.success(f"✅ Project '{name}' created!")
                    st.rerun()
                else:
                    st.error("❌ Failed. Check backend.")
