import streamlit as st
import requests
from datetime import date, timedelta

BACKEND = "http://localhost:5000"
st.set_page_config(page_title="Task Board — TeamSync", page_icon="✅", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:linear-gradient(135deg,#0d1117,#161b22,#0d1117);color:#e6edf3;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#161b22,#0d1117);border-right:1px solid #30363d;}
.badge{display:inline-block;padding:.2rem .6rem;border-radius:20px;font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:.04em;}
.badge-green{background:rgba(35,134,54,.2);color:#3fb950;border:1px solid #238636;}
.badge-red{background:rgba(218,54,51,.2);color:#f85149;border:1px solid #da3633;}
.badge-yellow{background:rgba(210,153,34,.2);color:#e3b341;border:1px solid #d29922;}
.badge-blue{background:rgba(31,111,235,.2);color:#58a6ff;border:1px solid #1f6feb;}
.badge-purple{background:rgba(188,106,255,.2);color:#bc6aff;border:1px solid #8b5cf6;}
.badge-gray{background:rgba(110,118,129,.2);color:#8b949e;border:1px solid #6e7681;}
.kanban-col{background:rgba(22,27,34,.6);border:1px solid #30363d;border-radius:12px;padding:1rem;min-height:400px;}
.kanban-card{background:rgba(13,17,23,.8);border:1px solid #30363d;border-radius:8px;padding:.9rem;margin-bottom:.6rem;transition:all .15s;}
.kanban-card:hover{border-color:#58a6ff;transform:translateY(-1px);}
.kanban-header{font-weight:600;font-size:.8rem;text-transform:uppercase;letter-spacing:.07em;margin-bottom:1rem;padding-bottom:.5rem;border-bottom:2px solid;}
.stButton>button{background:linear-gradient(135deg,#1f6feb,#388bfd);color:white;border:none;border-radius:8px;font-weight:600;}
.ts-form{background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:12px;padding:1.5rem;}
</style>""", unsafe_allow_html=True)


def api_get(path, params=None):
    try: return requests.get(f"{BACKEND}{path}", params=params, timeout=8).json()
    except: return None

def api_post(path, data):
    try: return requests.post(f"{BACKEND}{path}", json=data, timeout=8).json()
    except: return None

def api_put(path, data):
    try: return requests.put(f"{BACKEND}{path}", json=data, timeout=8).json()
    except: return None


PRIORITY_BADGE = {
    "critical": "badge-red", "high": "badge-yellow",
    "medium": "badge-blue", "low": "badge-gray",
}
STATUS_COLOR = {
    "todo": "#8b949e", "in_progress": "#58a6ff",
    "in_review": "#bc6aff", "completed": "#3fb950",
    "blocked": "#f85149",
}
STATUS_ICON = {
    "todo": "⬜", "in_progress": "🔄",
    "in_review": "👁", "completed": "✅", "blocked": "🚫",
}

st.markdown("""
<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid #21262d;margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#e6edf3;">✅ Kanban Task Board</div>
  <div style="font-size:.9rem;color:#8b949e;">Drag-and-drop task management · Online Examination System</div>
</div>
""", unsafe_allow_html=True)

tab_kanban, tab_list, tab_new = st.tabs(["📌 Kanban Board", "📋 Task List", "➕ New Task"])

with tab_kanban:
    tasks = api_get("/api/tasks/", {"project_id": 1})
    if not tasks:
        st.warning("⚠️ Backend offline. Start Flask server.")
        st.stop()

    columns = [
        ("todo", "⬜ To Do", "#8b949e"),
        ("in_progress", "🔄 In Progress", "#58a6ff"),
        ("in_review", "👁 In Review", "#bc6aff"),
        ("completed", "✅ Completed", "#3fb950"),
        ("blocked", "🚫 Blocked", "#f85149"),
    ]

    cols = st.columns(5)
    for col, (status, label, color) in zip(cols, columns):
        col_tasks = [t for t in tasks if t["status"] == status]
        with col:
            st.markdown(f"""
            <div class="kanban-col">
                <div class="kanban-header" style="color:{color};border-color:{color};">
                    {label} <span style="color:#8b949e;">({len(col_tasks)})</span>
                </div>
            """, unsafe_allow_html=True)

            for task in col_tasks:
                overdue_flag = "⚠️ " if task.get("is_overdue") else ""
                priority = task.get("priority", "medium")
                p_class = PRIORITY_BADGE.get(priority, "badge-gray")
                assignee = task.get("assignee_name", "Unassigned")
                due = task.get("due_date", "")[:10] if task.get("due_date") else "No date"

                st.markdown(f"""
                <div class="kanban-card">
                    <div style="font-weight:600;font-size:.85rem;margin-bottom:.4rem;">{overdue_flag}{task['title']}</div>
                    <div style="display:flex;gap:.4rem;flex-wrap:wrap;margin-bottom:.5rem;">
                        <span class="badge {p_class}">{priority}</span>
                        {'<span class="badge badge-red">overdue</span>' if task.get("is_overdue") else ''}
                        {f'<span class="badge badge-blue">#{task["github_issue_number"]}</span>' if task.get("github_issue_number") else ''}
                    </div>
                    <div style="font-size:.75rem;color:#8b949e;">👤 {assignee} · 📅 {due}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    # Quick status update
    st.markdown("---")
    st.markdown("#### ⚡ Quick Status Update")
    if tasks:
        task_options = {f"#{t['id']} — {t['title'][:40]}": t["id"] for t in tasks}
        c1, c2, c3 = st.columns([2, 1, 0.8])
        with c1:
            selected_task = st.selectbox("Select Task", list(task_options.keys()), key="quick_task")
        with c2:
            new_status = st.selectbox("New Status", ["todo", "in_progress", "in_review", "completed", "blocked"], key="quick_status")
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Update ✓"):
                task_id = task_options[selected_task]
                result = api_put(f"/api/tasks/{task_id}", {"status": new_status})
                if result:
                    st.success("✅ Task updated!")
                    st.rerun()

with tab_list:
    tasks = api_get("/api/tasks/", {"project_id": 1})
    if tasks:
        # Filters
        f1, f2, f3 = st.columns(3)
        with f1:
            status_filter = st.multiselect("Filter by Status", ["todo","in_progress","in_review","completed","blocked"], key="sf")
        with f2:
            priority_filter = st.multiselect("Filter by Priority", ["critical","high","medium","low"], key="pf")
        with f3:
            overdue_only = st.checkbox("Overdue Only", key="of")

        filtered = tasks
        if status_filter: filtered = [t for t in filtered if t["status"] in status_filter]
        if priority_filter: filtered = [t for t in filtered if t["priority"] in priority_filter]
        if overdue_only: filtered = [t for t in filtered if t.get("is_overdue")]

        st.markdown(f"**{len(filtered)} tasks**")
        for task in filtered:
            priority = task.get("priority","medium")
            p_class = PRIORITY_BADGE.get(priority, "badge-gray")
            s_color = STATUS_COLOR.get(task["status"], "#8b949e")
            s_icon = STATUS_ICON.get(task["status"], "•")
            overdue_html = '<span class="badge badge-red">OVERDUE</span>' if task.get("is_overdue") else ""

            with st.expander(f'{s_icon} {task["title"]} — {task.get("assignee_name","Unassigned")}'):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"""
                    <div style="margin-bottom:.8rem;">
                        <span class="badge {p_class}">{priority}</span>
                        <span class="badge" style="background:rgba(88,166,255,.1);color:{s_color};border-color:{s_color};">{task['status'].replace('_',' ')}</span>
                        {overdue_html}
                    </div>
                    <p style="color:#8b949e;font-size:.85rem;">{task.get('description','')}</p>
                    <div style="font-size:.8rem;color:#8b949e;">
                        📅 Due: {task.get('due_date','')[:10] if task.get('due_date') else '—'} &nbsp;|&nbsp;
                        👤 {task.get('assignee_name','Unassigned')} &nbsp;|&nbsp;
                        {f'🐛 Issue #{task["github_issue_number"]}' if task.get("github_issue_number") else ''}
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    new_st = st.selectbox("Status", ["todo","in_progress","in_review","completed","blocked"],
                                           index=["todo","in_progress","in_review","completed","blocked"].index(task["status"]),
                                           key=f"status_{task['id']}")
                    if st.button("Save", key=f"save_{task['id']}"):
                        api_put(f"/api/tasks/{task['id']}", {"status": new_st})
                        st.success("Updated!")
                        st.rerun()

with tab_new:
    st.markdown("#### ➕ Create New Task")
    users_data = api_get("/api/auth/users")

    with st.form("new_task_form"):
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("Task Title *", placeholder="e.g., Implement OAuth2 Login")
            description = st.text_area("Description", placeholder="Detailed description of the task...")
            priority = st.selectbox("Priority", ["low","medium","high","critical"])
        with c2:
            status = st.selectbox("Initial Status", ["todo","in_progress"])
            due_date = st.date_input("Due Date", value=date.today() + timedelta(days=7))
            users_list = users_data if users_data else []
            user_opts = {u["name"]: u["id"] for u in users_list}
            assignee_name = st.selectbox("Assign To", ["Unassigned"] + list(user_opts.keys()))
            gh_issue = st.number_input("Link GitHub Issue #", min_value=0, value=0)
            est_hours = st.number_input("Estimated Hours", min_value=0.5, max_value=200.0, value=4.0, step=0.5)

        if st.form_submit_button("🚀 Create Task", use_container_width=True):
            if not title:
                st.error("Title is required!")
            else:
                payload = {
                    "project_id": 1,
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "status": status,
                    "due_date": due_date.isoformat(),
                    "assigned_user_id": user_opts.get(assignee_name) if assignee_name != "Unassigned" else None,
                    "github_issue_number": gh_issue if gh_issue > 0 else None,
                    "estimated_hours": est_hours,
                }
                result = api_post("/api/tasks/", payload)
                if result and "id" in result:
                    st.success(f"✅ Task created: #{result['id']} — {title}")
                    st.rerun()
                else:
                    st.error("❌ Failed to create task. Check backend.")
