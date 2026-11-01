import streamlit as st

BACKEND = "http://localhost:5000"
st.set_page_config(page_title="Notifications — TeamSync", page_icon="🔔", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:linear-gradient(135deg,#0d1117,#161b22,#0d1117);color:#e6edf3;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#161b22,#0d1117);border-right:1px solid #30363d;}
.notif-card{background:rgba(22,27,34,.9);border-left:3px solid;border-radius:0 10px 10px 0;
  padding:1rem 1.3rem;margin-bottom:.5rem;border-top:1px solid #21262d;
  border-right:1px solid #21262d;border-bottom:1px solid #21262d;transition:all .15s;}
.notif-card:hover{background:rgba(30,36,44,.9);}
.notif-card.unread{background:rgba(22,27,34,.99);}
.badge{display:inline-block;padding:.15rem .5rem;border-radius:12px;font-size:.7rem;font-weight:600;text-transform:uppercase;}
</style>""", unsafe_allow_html=True)

st.markdown("""
<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid #21262d;margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#e6edf3;">🔔 Notifications</div>
  <div style="font-size:.9rem;color:#8b949e;">Task assignments · Deadline alerts · CI failures · PR reviews</div>
</div>
""", unsafe_allow_html=True)

# Demo notifications
notifications = [
    {"type":"error","category":"quality","title":"❌ CI Failed — PR #13 (feature/exam-module)","message":"Ruff found 12 linting issues. Bandit and Pytest were skipped. Fix linting before requesting review.","time":"2 min ago","read":False},
    {"type":"warning","category":"deadline","title":"⚠️ Task Overdue — Result Generation Engine","message":"This task assigned to Sneha Patel was due yesterday. Current status: To Do. Action required.","time":"1 hour ago","read":False},
    {"type":"warning","category":"pr","title":"⏳ PR #15 has changes requested","message":"Priya Sharma requested changes on 'test: Pytest suite for auth module'. Review comments added.","time":"3 hours ago","read":False},
    {"type":"info","category":"pr","title":"🔀 PR #12 Merged Successfully","message":"'feat: Complete JWT authentication system' was merged into main by Arjun Mehta. All checks passed.","time":"1 day ago","read":True},
    {"type":"success","category":"quality","title":"✅ CI Passed — PR #15 (feature/tests)","message":"All GitHub Actions checks passed: Ruff ✅ Pytest 42/42 ✅. Ready for review.","time":"1 day ago","read":True},
    {"type":"info","category":"task","title":"📋 New Task Assigned — Unit Test Suite","message":"Rohan Gupta, you have been assigned 'Unit Test Suite' (High Priority). Due in 2 days.","time":"2 days ago","read":True},
    {"type":"error","category":"quality","title":"🔒 Security Issue — Bandit Warning","message":"Bandit detected a potential hardcoded password in backend/config.py (line 45). Review immediately.","time":"3 days ago","read":True},
    {"type":"info","category":"deadline","title":"📅 Milestone 'Backend API v1' due in 5 days","message":"Milestone has 5 open issues and 3 closed. 37.5% complete. Accelerate to meet deadline.","time":"3 days ago","read":True},
]

col1, col2 = st.columns([3, 1])
with col2:
    filter_type = st.selectbox("Filter", ["All","Unread","error","warning","info","success"])
    if st.button("Mark All Read"):
        st.success("All notifications marked as read!")

unread_count = len([n for n in notifications if not n["read"]])
with col1:
    st.markdown(f"""
    <div style="font-size:.9rem;color:#8b949e;">
        <span style="background:#da3633;color:white;border-radius:50%;padding:.1rem .4rem;
            font-size:.72rem;font-weight:700;margin-right:.4rem;">{unread_count}</span>
        Unread notifications
    </div>
    """, unsafe_allow_html=True)

filtered = notifications
if filter_type == "Unread": filtered = [n for n in notifications if not n["read"]]
elif filter_type in ("error","warning","info","success"): filtered = [n for n in notifications if n["type"]==filter_type]

type_config = {
    "error": ("#da3633", "#f85149"),
    "warning": ("#d29922", "#e3b341"),
    "info": ("#1f6feb", "#58a6ff"),
    "success": ("#238636", "#3fb950"),
}

for notif in filtered:
    border_color, text_color = type_config.get(notif["type"], ("#30363d","#8b949e"))
    unread_class = "unread" if not notif["read"] else ""
    unread_dot = '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#58a6ff;margin-right:.4rem;"></span>' if not notif["read"] else ""
    cat_colors = {"quality":"#bc6aff","deadline":"#e3b341","pr":"#58a6ff","task":"#3fb950","issue":"#f85149"}

    st.markdown(f"""
    <div class="notif-card {unread_class}" style="border-left-color:{border_color};">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div style="flex:1;">
                <div style="font-weight:600;font-size:.9rem;color:#e6edf3;margin-bottom:.3rem;">
                    {unread_dot}{notif['title']}
                </div>
                <div style="font-size:.82rem;color:#8b949e;">{notif['message']}</div>
            </div>
            <div style="text-align:right;margin-left:1rem;">
                <div style="font-size:.72rem;color:#8b949e;">{notif['time']}</div>
                <span style="display:inline-block;background:rgba({','.join(str(int(cat_colors.get(notif['category'],'#8b949e').lstrip('#')[i:i+2],16)) for i in (0,2,4))},.15);
                    color:{cat_colors.get(notif['category'],'#8b949e')};border-radius:12px;
                    padding:.1rem .4rem;font-size:.68rem;font-weight:600;text-transform:uppercase;
                    margin-top:.2rem;">{notif['category']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
