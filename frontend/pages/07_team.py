import streamlit as st
import requests
import plotly.graph_objects as go

BACKEND = "http://localhost:5000"
st.set_page_config(page_title="Team — TeamSync", page_icon="👥", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:linear-gradient(135deg,#0d1117,#161b22,#0d1117);color:#e6edf3;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#161b22,#0d1117);border-right:1px solid #30363d;}
.member-card{background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:14px;
  padding:1.5rem;text-align:center;transition:all .2s;}
.member-card:hover{border-color:#58a6ff;transform:translateY(-3px);box-shadow:0 8px 28px rgba(88,166,255,.12);}
.avatar{width:70px;height:70px;border-radius:50%;background:linear-gradient(135deg,#1f6feb,#bc6aff);
  display:flex;align-items:center;justify-content:center;font-size:1.8rem;margin:0 auto .8rem;}
.role-badge{display:inline-block;padding:.25rem .7rem;border-radius:20px;font-size:.72rem;
  font-weight:600;text-transform:uppercase;letter-spacing:.05em;}
.role-lead{background:rgba(188,106,255,.2);color:#bc6aff;border:1px solid #8b5cf6;}
.role-developer{background:rgba(31,111,235,.2);color:#58a6ff;border:1px solid #1f6feb;}
.role-qa{background:rgba(210,153,34,.2);color:#e3b341;border:1px solid #d29922;}
.role-viewer{background:rgba(110,118,129,.2);color:#8b949e;border:1px solid #6e7681;}
.stat-mini{display:inline-block;background:rgba(13,17,23,.8);border:1px solid #30363d;
  border-radius:8px;padding:.4rem .8rem;font-size:.8rem;margin:.2rem;}
.progress-wrap{background:#21262d;border-radius:4px;height:6px;width:100%;overflow:hidden;}
.stButton>button{background:linear-gradient(135deg,#1f6feb,#388bfd);color:white;border:none;border-radius:8px;font-weight:600;}
</style>""", unsafe_allow_html=True)


def api_get(p, params=None):
    try: return requests.get(f"{BACKEND}{p}", params=params, timeout=8).json()
    except: return None


AVATARS = ["👩‍💻","👨‍💻","👩‍💼","👨‍🔬","👩‍🔬"]
ROLE_CLASS = {"lead":"role-lead","developer":"role-developer","qa":"role-qa","viewer":"role-viewer"}

st.markdown("""
<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid #21262d;margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#e6edf3;">👥 Team Management</div>
  <div style="font-size:.9rem;color:#8b949e;">Members · Roles · Workload · Task distribution</div>
</div>
""", unsafe_allow_html=True)

tab_team, tab_workload, tab_add = st.tabs(["👥 Team Members", "📊 Workload Analytics", "➕ Add Member"])

with tab_team:
    members = api_get("/api/team/members", {"project_id": 1})
    if not members:
        st.warning("No team data.")
        st.stop()

    cols = st.columns(min(len(members), 3))
    for i, m in enumerate(members):
        user = m.get("user", m)
        role = m.get("role", user.get("role","developer"))
        role_class = ROLE_CLASS.get(role, "role-developer")
        avatar = AVATARS[i % len(AVATARS)]
        gh = user.get("github_username","")

        with cols[i % 3]:
            st.markdown(f"""
            <div class="member-card">
                <div class="avatar">{avatar}</div>
                <div style="font-weight:700;font-size:1rem;margin-bottom:.3rem;">{user.get('name','')}</div>
                <span class="role-badge {role_class}">{role}</span>
                <div style="margin:.6rem 0;font-size:.8rem;color:#8b949e;">
                    {f'<a href="https://github.com/{gh}" target="_blank" style="color:#58a6ff;text-decoration:none;">@{gh}</a>' if gh else '—'}
                </div>
                <div style="font-size:.78rem;color:#8b949e;">{user.get('email','')}</div>
            </div>
            """, unsafe_allow_html=True)

with tab_workload:
    workload = api_get("/api/analytics/workload", {"project_id": 1})
    if not workload:
        st.warning("No workload data.")
    else:
        # Summary
        st.markdown("#### 📊 Developer Task Distribution")

        names = [w["name"].split()[0] for w in workload]
        totals = [w["total_tasks"] for w in workload]
        completed_list = [w["completed"] for w in workload]
        in_progress_list = [w["in_progress"] for w in workload]
        overdue_list = [w["overdue"] for w in workload]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Completed", x=names, y=completed_list, marker_color="#3fb950",
                             text=completed_list, textposition="inside", textfont_size=11))
        fig.add_trace(go.Bar(name="In Progress", x=names, y=in_progress_list, marker_color="#58a6ff"))
        fig.add_trace(go.Bar(name="Remaining", x=names,
                             y=[max(0, t-c-i) for t,c,i in zip(totals,completed_list,in_progress_list)],
                             marker_color="#30363d"))
        fig.update_layout(
            barmode="stack", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e6edf3", height=280, margin=dict(l=10,r=10,t=20,b=10),
            xaxis=dict(showgrid=False,color="#8b949e"),
            yaxis=dict(showgrid=True,gridcolor="#21262d",color="#8b949e",title="Tasks"),
            legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#8b949e",size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📋 Individual Breakdown")
        for w in workload:
            comp_rate = w["completion_rate"]
            color = "#3fb950" if comp_rate >= 75 else "#58a6ff" if comp_rate >= 40 else "#e3b341"
            overdue_html = f'<span style="color:#f85149;font-size:.8rem;">⚠️ {w["overdue"]} overdue</span>' if w["overdue"] > 0 else ""

            st.markdown(f"""
            <div style="background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:10px;
                padding:1rem 1.3rem;margin-bottom:.7rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem;">
                    <div>
                        <span style="font-weight:600;font-size:.95rem;">{w['name']}</span>
                        <span style="color:#8b949e;font-size:.8rem;margin-left:.5rem;">· {w.get('role','developer')}</span>
                    </div>
                    <div style="display:flex;gap:.5rem;align-items:center;">
                        <span class="stat-mini" style="color:#e6edf3;">{w['total_tasks']} tasks</span>
                        <span class="stat-mini" style="color:#3fb950;">{w['completed']} done</span>
                        <span class="stat-mini" style="color:#58a6ff;">{w['in_progress']} active</span>
                        {overdue_html}
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap.8rem;">
                    <div class="progress-wrap" style="flex:1;">
                        <div style="width:{comp_rate}%;height:100%;background:{color};border-radius:4px;"></div>
                    </div>
                    <span style="color:{color};font-weight:700;font-size:.9rem;margin-left:.8rem;">{comp_rate}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab_add:
    st.markdown("#### ➕ Add Team Member")
    all_users = api_get("/api/auth/users")

    with st.form("add_member_form"):
        if all_users:
            user_opts = {u["name"]: u["id"] for u in all_users}
            selected_user = st.selectbox("Select User", list(user_opts.keys()))
        else:
            selected_user = st.text_input("User ID")
            user_opts = {}
        role = st.selectbox("Project Role", ["developer","lead","qa","viewer"])

        if st.form_submit_button("➕ Add to Project"):
            user_id = user_opts.get(selected_user, selected_user)
            r = requests.post(f"{BACKEND}/api/projects/1/members",
                              json={"user_id": user_id, "role": role}, timeout=8)
            if r.status_code in (200,201):
                st.success("✅ Member added!")
                st.rerun()
            elif r.status_code == 409:
                st.warning("User already a member.")
            else:
                st.error("❌ Failed.")
