import streamlit as st
import requests

BACKEND = "http://localhost:5000"
st.set_page_config(page_title="Pull Requests — TeamSync", page_icon="🔀", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:linear-gradient(135deg,#0d1117,#161b22,#0d1117);color:#e6edf3;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#161b22,#0d1117);border-right:1px solid #30363d;}
.pr-card{background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:12px;
  padding:1rem 1.3rem;margin-bottom:.7rem;transition:all .2s;}
.pr-card:hover{border-color:#58a6ff;box-shadow:0 4px 18px rgba(88,166,255,.1);}
.badge{display:inline-block;padding:.2rem .6rem;border-radius:20px;font-size:.72rem;font-weight:600;
  text-transform:uppercase;letter-spacing:.04em;}
.badge-green{background:rgba(35,134,54,.2);color:#3fb950;border:1px solid #238636;}
.badge-red{background:rgba(218,54,51,.2);color:#f85149;border:1px solid #da3633;}
.badge-yellow{background:rgba(210,153,34,.2);color:#e3b341;border:1px solid #d29922;}
.badge-blue{background:rgba(31,111,235,.2);color:#58a6ff;border:1px solid #1f6feb;}
.badge-purple{background:rgba(188,106,255,.2);color:#bc6aff;border:1px solid #8b5cf6;}
.badge-gray{background:rgba(110,118,129,.2);color:#8b949e;border:1px solid #6e7681;}
.ts-card{background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem;}
.metric-box{background:rgba(13,17,23,.8);border:1px solid #30363d;border-radius:10px;padding:1rem;text-align:center;}
</style>""", unsafe_allow_html=True)


def api_get(p, params=None):
    try: return requests.get(f"{BACKEND}{p}", params=params, timeout=8).json()
    except: return []


REVIEW_BADGE = {
    "approved": ("badge-green", "✅ Approved"),
    "changes_requested": ("badge-red", "🔄 Changes Requested"),
    "pending": ("badge-yellow", "⏳ Awaiting Review"),
}
CHECK_BADGE = {
    "passed": ("badge-green", "✅ Checks Passed"),
    "failed": ("badge-red", "❌ Checks Failed"),
    "pending": ("badge-yellow", "⏳ Checks Running"),
}

st.markdown("""
<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid #21262d;margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#e6edf3;">🔀 Pull Requests</div>
  <div style="font-size:.9rem;color:#8b949e;">Code review status · CI checks · Merge tracking</div>
</div>
""", unsafe_allow_html=True)

prs = api_get("/api/github/pull-requests", {"project_id": 1})
if not prs:
    st.warning("⚠️ No PR data. Start backend.")
    st.stop()

# ─── Summary Metrics ─────────────────────────────────────────────────────────
open_prs = [pr for pr in prs if pr["state"] == "open" and not pr["merged"]]
merged_prs = [pr for pr in prs if pr["merged"]]
pending_review = [pr for pr in open_prs if pr.get("review_status") == "pending"]
failed_checks = [pr for pr in open_prs if pr.get("check_status") == "failed"]
approved_prs = [pr for pr in open_prs if pr.get("review_status") == "approved"]

cols = st.columns(5)
metrics = [
    ("🔀", len(open_prs), "Open PRs", "#58a6ff"),
    ("✅", len(merged_prs), "Merged", "#3fb950"),
    ("⏳", len(pending_review), "Awaiting Review", "#e3b341"),
    ("❌", len(failed_checks), "CI Failed", "#f85149"),
    ("👍", len(approved_prs), "Approved", "#3fb950"),
]
for col, (icon, val, lbl, color) in zip(cols, metrics):
    with col:
        st.markdown(f"""
        <div class="metric-box">
            <div style="font-size:1.4rem;">{icon}</div>
            <div style="font-size:2rem;font-weight:800;color:{color};">{val}</div>
            <div style="font-size:.73rem;color:#8b949e;text-transform:uppercase;letter-spacing:.06em;">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Filters ─────────────────────────────────────────────────────────────────
f1, f2, f3 = st.columns(3)
with f1: state_f = st.selectbox("State", ["All","Open","Merged","Closed"])
with f2: review_f = st.selectbox("Review Status", ["All","pending","approved","changes_requested"])
with f3: check_f = st.selectbox("CI Status", ["All","passed","failed","pending"])

filtered_prs = prs
if state_f == "Open": filtered_prs = [pr for pr in filtered_prs if pr["state"]=="open" and not pr["merged"]]
elif state_f == "Merged": filtered_prs = [pr for pr in filtered_prs if pr["merged"]]
elif state_f == "Closed": filtered_prs = [pr for pr in filtered_prs if pr["state"]=="closed" and not pr["merged"]]
if review_f != "All": filtered_prs = [pr for pr in filtered_prs if pr.get("review_status")==review_f]
if check_f != "All": filtered_prs = [pr for pr in filtered_prs if pr.get("check_status")==check_f]

st.markdown(f"**{len(filtered_prs)} pull requests**")
st.markdown("---")

# ─── PR List ─────────────────────────────────────────────────────────────────
for pr in filtered_prs:
    pr_num = pr.get("github_pr_number","?")
    title = pr.get("title","")
    author = pr.get("author","Unknown")
    head = pr.get("head_branch","?")
    base = pr.get("base_branch","main")
    additions = pr.get("additions",0)
    deletions = pr.get("deletions",0)
    changed = pr.get("changed_files",0)
    github_url = pr.get("github_url","#")

    review_class, review_lbl = REVIEW_BADGE.get(pr.get("review_status","pending"), ("badge-gray","—"))
    check_class, check_lbl = CHECK_BADGE.get(pr.get("check_status","pending"), ("badge-gray","—"))

    state_icon = "🟣 Merged" if pr.get("merged") else "🟢 Open" if pr["state"]=="open" else "🔴 Closed"
    draft_badge = '<span class="badge badge-gray">Draft</span>' if pr.get("draft") else ""

    st.markdown(f"""
    <div class="pr-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.5rem;">
            <div style="flex:1;">
                <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.3rem;">
                    <span style="font-size:.8rem;color:#8b949e;">#{pr_num}</span>
                    <a href="{github_url}" target="_blank"
                       style="font-weight:600;font-size:.95rem;color:#e6edf3;text-decoration:none;">
                        {title}
                    </a>
                    {draft_badge}
                </div>
                <div style="font-size:.78rem;color:#8b949e;">
                    👤 <strong style="color:#e6edf3;">{author}</strong> &nbsp;·&nbsp;
                    <code style="color:#58a6ff;background:rgba(31,111,235,.1);padding:.1rem .3rem;border-radius:4px;">{head}</code>
                    → <code style="color:#3fb950;background:rgba(35,134,54,.1);padding:.1rem .3rem;border-radius:4px;">{base}</code>
                    &nbsp;·&nbsp; 📁 {changed} files &nbsp;
                    <span style="color:#3fb950;">+{additions}</span> / <span style="color:#f85149;">-{deletions}</span>
                </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:.3rem;align-items:flex-end;">
                <span class="badge {'badge-purple' if pr.get('merged') else 'badge-green' if pr['state']=='open' else 'badge-gray'}">{state_icon}</span>
                <span class="badge {review_class}">{review_lbl}</span>
                <span class="badge {check_class}">{check_lbl}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Alert Section ────────────────────────────────────────────────────────────
if failed_checks or pending_review:
    st.markdown("---")
    st.markdown("#### ⚠️ Action Required")
    if failed_checks:
        st.markdown(f"""
        <div style="background:rgba(218,54,51,.08);border:1px solid #da3633;border-radius:8px;padding:1rem;margin-bottom:.5rem;">
            <strong style="color:#f85149;">❌ {len(failed_checks)} PR(s) have failing CI checks</strong><br>
            <span style="font-size:.83rem;color:#8b949e;">Review and fix test failures before merge.</span>
        </div>
        """, unsafe_allow_html=True)
    if pending_review:
        st.markdown(f"""
        <div style="background:rgba(210,153,34,.08);border:1px solid #d29922;border-radius:8px;padding:1rem;">
            <strong style="color:#e3b341;">⏳ {len(pending_review)} PR(s) are awaiting code review</strong><br>
            <span style="font-size:.83rem;color:#8b949e;">Assign reviewers and complete review.</span>
        </div>
        """, unsafe_allow_html=True)
