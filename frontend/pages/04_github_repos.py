import streamlit as st
import requests

BACKEND = "http://localhost:5000"
st.set_page_config(page_title="GitHub Repos — TeamSync", page_icon="🐙", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:linear-gradient(135deg,#0d1117,#161b22,#0d1117);color:#e6edf3;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#161b22,#0d1117);border-right:1px solid #30363d;}
.ts-card{background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:12px;padding:1.2rem 1.5rem;
  margin-bottom:1rem;transition:all .2s;}
.ts-card:hover{border-color:#58a6ff;box-shadow:0 4px 24px rgba(88,166,255,.1);}
.commit-row{background:rgba(13,17,23,.6);border:1px solid #21262d;border-radius:8px;
  padding:.6rem 1rem;margin-bottom:.4rem;font-size:.83rem;}
.branch-chip{display:inline-block;background:rgba(31,111,235,.15);color:#58a6ff;
  border:1px solid #1f6feb;border-radius:20px;padding:.2rem .7rem;font-size:.75rem;
  margin:.2rem;font-family:monospace;}
.protected-chip{background:rgba(35,134,54,.15);color:#3fb950;border-color:#238636;}
.lang-bar{height:8px;border-radius:4px;margin-bottom:.2rem;}
.stat-box{background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:10px;
  padding:1rem;text-align:center;}
.stat-num{font-size:2rem;font-weight:800;}
.stat-lbl{font-size:.75rem;color:#8b949e;text-transform:uppercase;letter-spacing:.06em;}
.stButton>button{background:linear-gradient(135deg,#1f6feb,#388bfd);color:white;border:none;
  border-radius:8px;font-weight:600;}
</style>""", unsafe_allow_html=True)


def api_get(p, params=None):
    try: return requests.get(f"{BACKEND}{p}", params=params, timeout=10).json()
    except: return None


LANG_COLORS = {
    "Python":"#3572A5","JavaScript":"#f1e05a","TypeScript":"#2b7489",
    "HTML":"#e34c26","CSS":"#563d7c","Java":"#b07219","Go":"#00ADD8",
    "Rust":"#dea584","Shell":"#89e051","Other":"#8b949e",
}

st.markdown("""
<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid #21262d;margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#e6edf3;">🐙 GitHub Repository</div>
  <div style="font-size:.9rem;color:#8b949e;">Connected repository · Branches · Commits · Languages</div>
</div>
""", unsafe_allow_html=True)

# Repo input
c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    owner = st.text_input("GitHub Owner", value="teamsync-demo", placeholder="owner")
with c2:
    repo = st.text_input("Repository Name", value="online-exam-system", placeholder="repo-name")
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    fetch_btn = st.button("🔍 Fetch / Demo", use_container_width=True)

data = api_get("/api/github/repo", {"owner": owner, "repo": repo})

if not data:
    st.warning("⚠️ Backend offline.")
    st.stop()

repo_info = data.get("repository", {})
stats = data.get("stats", {})
commits = data.get("recent_commits", [])
branches = data.get("branches", [])
languages = data.get("languages", {})

# ─── Repo Header ─────────────────────────────────────────────────────────────
if repo_info:
    is_private = repo_info.get("private", False)
    vis = "🔒 Private" if is_private else "🌐 Public"
    html_url = repo_info.get("html_url", f"https://github.com/{owner}/{repo}")

    st.markdown(f"""
    <div class="ts-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
                <div style="display:flex;align-items:center;gap:.8rem;">
                    <span style="font-size:1.5rem;">🐙</span>
                    <a href="{html_url}" target="_blank"
                       style="font-size:1.3rem;font-weight:700;color:#58a6ff;text-decoration:none;">
                        {repo_info.get('full_name', f'{owner}/{repo}')}
                    </a>
                    <span style="font-size:.75rem;background:rgba(110,118,129,.2);color:#8b949e;
                        border:1px solid #6e7681;border-radius:20px;padding:.15rem .5rem;">{vis}</span>
                </div>
                <div style="font-size:.9rem;color:#8b949e;margin-top:.4rem;">
                    {repo_info.get('description','No description')}
                </div>
            </div>
            <div style="text-align:right;font-size:.8rem;color:#8b949e;">
                🌿 Default: <code style="color:#58a6ff;">{stats.get('default_branch','main')}</code><br>
                Updated: {repo_info.get('pushed_at','')[:10] if repo_info.get('pushed_at') else '—'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Stats Row ───────────────────────────────────────────────────────────────
stat_cols = st.columns(7)
stat_items = [
    ("⭐", stats.get("stars",0), "Stars"),
    ("🍴", stats.get("forks",0), "Forks"),
    ("👁", stats.get("watchers",0), "Watchers"),
    ("🌿", stats.get("branches",0), "Branches"),
    ("🐛", stats.get("open_issues",0), "Open Issues"),
    ("🔀", stats.get("open_prs",0), "Open PRs"),
    ("✅", stats.get("merged_prs",0), "Merged PRs"),
]
for col, (icon, val, lbl) in zip(stat_cols, stat_items):
    with col:
        st.markdown(f"""
        <div class="stat-box">
            <div style="font-size:1.3rem;">{icon}</div>
            <div class="stat-num" style="color:#58a6ff;font-size:1.6rem;">{val}</div>
            <div class="stat-lbl">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Language + Branches + Commits ───────────────────────────────────────────
col_lang, col_branch = st.columns([1.5, 2])

with col_lang:
    st.markdown('<div class="ts-card">', unsafe_allow_html=True)
    st.markdown("#### 💻 Languages")
    if languages:
        total_bytes = sum(languages.values())
        for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            pct = round(bytes_count / total_bytes * 100, 1)
            color = LANG_COLORS.get(lang, "#8b949e")
            st.markdown(f"""
            <div style="margin-bottom:.6rem;">
                <div style="display:flex;justify-content:space-between;font-size:.82rem;margin-bottom:.25rem;">
                    <span style="color:#e6edf3;font-weight:500;">
                        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
                            background:{color};margin-right:.4rem;"></span>{lang}
                    </span>
                    <span style="color:#8b949e;">{pct}%</span>
                </div>
                <div class="lang-bar" style="background:#21262d;">
                    <div style="width:{pct}%;height:100%;background:{color};border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_branch:
    st.markdown('<div class="ts-card">', unsafe_allow_html=True)
    st.markdown(f"#### 🌿 Branches ({len(branches)})")
    if branches:
        for b in branches:
            protected = b.get("protected", False)
            chip_class = "branch-chip protected-chip" if protected else "branch-chip"
            lock = "🔒 " if protected else ""
            st.markdown(f'<span class="{chip_class}">{lock}{b["name"]}</span>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Recent Commits ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 📦 Recent Commits")

if commits:
    for c in commits:
        sha = c.get("sha","")[:7]
        msg = c.get("commit",{}).get("message","").split("\n")[0]
        author = c.get("commit",{}).get("author",{}).get("name","Unknown")
        date_str = c.get("commit",{}).get("author",{}).get("date","")[:10]

        st.markdown(f"""
        <div class="commit-row">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="flex:1;">
                    <span style="font-family:monospace;color:#bc6aff;font-size:.8rem;">⬡ {sha}</span>
                    &nbsp; <span style="color:#e6edf3;">{msg}</span>
                </div>
                <div style="text-align:right;font-size:.78rem;color:#8b949e;white-space:nowrap;">
                    👤 {author} · {date_str}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── Sync Button ─────────────────────────────────────────────────────────────
st.markdown("---")
col_sync1, col_sync2 = st.columns([1, 4])
with col_sync1:
    if st.button("🔄 Sync with GitHub", use_container_width=True):
        try:
            result = requests.post(f"{BACKEND}/api/github/sync/1", timeout=15).json()
            if "error" in result:
                st.warning(f"⚠️ {result['error']}")
            else:
                st.success(f"✅ Synced! {result.get('issues',0)} issues, {result.get('prs',0)} PRs updated.")
        except:
            st.error("❌ Sync failed — backend may be offline.")
with col_sync2:
    st.markdown('<div style="font-size:.82rem;color:#8b949e;padding-top:.6rem;">Fetches latest Issues, Pull Requests, and check results from GitHub API and updates the local database.</div>', unsafe_allow_html=True)
