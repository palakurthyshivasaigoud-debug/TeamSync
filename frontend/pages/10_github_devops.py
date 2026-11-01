import streamlit as st
import requests

BACKEND = "http://localhost:5000"
st.set_page_config(page_title="GitHub DevOps — TeamSync", page_icon="⚡", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:linear-gradient(135deg,#0d1117,#161b22,#0d1117);color:#e6edf3;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#161b22,#0d1117);border-right:1px solid #30363d;}

/* Concept cards */
.concept-card{background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:14px;
  padding:1.5rem;margin-bottom:1rem;transition:all .2s;}
.concept-card:hover{border-color:#58a6ff;box-shadow:0 4px 24px rgba(88,166,255,.1);}
.concept-icon{font-size:2.5rem;margin-bottom:.8rem;}
.concept-title{font-size:1.1rem;font-weight:700;color:#e6edf3;margin-bottom:.4rem;}
.concept-desc{font-size:.83rem;color:#8b949e;line-height:1.5;}

/* Pipeline steps */
.pipeline-step{background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:10px;
  padding:1rem;text-align:center;position:relative;transition:all .2s;}
.pipeline-step.success{border-color:#238636;background:rgba(35,134,54,.06);}
.pipeline-step.failure{border-color:#da3633;background:rgba(218,54,51,.06);}
.pipeline-step.running{border-color:#d29922;background:rgba(210,153,34,.06);}
.pipeline-step.pending{border-color:#30363d;background:rgba(22,27,34,.4);}
.pipeline-arrow{color:#30363d;font-size:1.5rem;text-align:center;padding:0 .3rem;}

/* Workflow run rows */
.run-row{background:rgba(13,17,23,.7);border:1px solid #21262d;border-radius:8px;
  padding:.8rem 1rem;margin-bottom:.4rem;transition:background .15s;}
.run-row:hover{background:rgba(22,27,34,.9);}

/* Terminal */
.terminal{background:#0d1117;border:1px solid #30363d;border-radius:10px;
  font-family:'JetBrains Mono',monospace;font-size:.8rem;padding:1rem;
  overflow-x:auto;line-height:1.6;min-height:120px;}
.t-green{color:#3fb950;}
.t-red{color:#f85149;}
.t-yellow{color:#e3b341;}
.t-blue{color:#58a6ff;}
.t-purple{color:#bc6aff;}
.t-gray{color:#8b949e;}
.t-white{color:#e6edf3;}
.t-prompt{color:#3fb950;}

/* Git graph */
.git-graph{font-family:'JetBrains Mono',monospace;font-size:.78rem;
  background:#0d1117;border:1px solid #30363d;border-radius:8px;
  padding:1rem;line-height:1.7;}

/* Badge */
.badge{display:inline-block;padding:.2rem .6rem;border-radius:20px;font-size:.72rem;
  font-weight:600;text-transform:uppercase;letter-spacing:.04em;}
.badge-green{background:rgba(35,134,54,.2);color:#3fb950;border:1px solid #238636;}
.badge-red{background:rgba(218,54,51,.2);color:#f85149;border:1px solid #da3633;}
.badge-yellow{background:rgba(210,153,34,.2);color:#e3b341;border:1px solid #d29922;}
.badge-blue{background:rgba(31,111,235,.2);color:#58a6ff;border:1px solid #1f6feb;}
.badge-purple{background:rgba(188,106,255,.2);color:#bc6aff;border:1px solid #8b5cf6;}
.badge-gray{background:rgba(110,118,129,.2);color:#8b949e;border:1px solid #6e7681;}

/* GitHub Foundations chip */
.gf-chip{display:inline-block;background:rgba(31,111,235,.1);color:#58a6ff;
  border:1px solid rgba(31,111,235,.4);border-radius:6px;padding:.2rem .5rem;
  font-size:.7rem;font-weight:600;margin:.15rem;}

/* Section divider */
.section-divider{display:flex;align-items:center;gap:1rem;margin:1.5rem 0;}
.section-divider-line{flex:1;height:1px;background:#21262d;}
.section-divider-text{font-size:.75rem;color:#8b949e;text-transform:uppercase;letter-spacing:.1em;white-space:nowrap;}

.stButton>button{background:linear-gradient(135deg,#1f6feb,#388bfd);color:white;
  border:none;border-radius:8px;font-weight:600;transition:all .2s;}
.stButton>button:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(88,166,255,.3);}

/* Distinction banner */
.distinction-banner{background:linear-gradient(135deg,rgba(31,111,235,.12),rgba(188,106,255,.12));
  border:1px solid rgba(88,166,255,.3);border-radius:14px;padding:1.5rem;margin-bottom:1.5rem;}

/* CI steps */
.ci-step{display:flex;align-items:center;gap:.8rem;padding:.7rem 1rem;border-radius:8px;
  border:1px solid #21262d;margin-bottom:.3rem;background:rgba(13,17,23,.5);transition:all .2s;}
.ci-step.success-step{border-color:#238636;background:rgba(35,134,54,.05);}
.ci-step.failure-step{border-color:#da3633;background:rgba(218,54,51,.05);}
.ci-step.running-step{border-color:#d29922;background:rgba(210,153,34,.05);}

/* Webhook event */
.webhook-event{background:rgba(13,17,23,.7);border-left:3px solid #58a6ff;border-radius:0 8px 8px 0;
  border-top:1px solid #21262d;border-right:1px solid #21262d;border-bottom:1px solid #21262d;
  padding:.7rem 1rem;margin-bottom:.4rem;font-family:'JetBrains Mono',monospace;font-size:.78rem;}
</style>""", unsafe_allow_html=True)


def api_get(p, params=None):
    try: return requests.get(f"{BACKEND}{p}", params=params, timeout=8).json()
    except: return None


# ─── Page Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid #21262d;margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#e6edf3;">⚡ GitHub DevOps & Automation</div>
  <div style="font-size:.9rem;color:#8b949e;">
    Demonstrating Git operations, GitHub Actions CI/CD, webhooks, and branching strategy
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Key Distinction Banner ────────────────────────────────────────────────────
st.markdown("""
<div class="distinction-banner">
    <div style="font-size:1rem;font-weight:700;color:#58a6ff;margin-bottom:.8rem;">
        ⚡ Two Distinct Concepts — Both Demonstrated Here
    </div>
    <div style="display:flex;gap:2rem;">
        <div style="flex:1;">
            <div style="font-weight:600;color:#e6edf3;margin-bottom:.3rem;">
                🌿 Part 1: Git Operations
            </div>
            <div style="font-size:.83rem;color:#8b949e;">
                Creating branches, committing changes, pushing code to GitHub.
                These are <em>developer actions</em> done locally or via GitHub.
            </div>
            <div style="margin-top:.5rem;">
                <span class="gf-chip">Repository</span>
                <span class="gf-chip">Branch</span>
                <span class="gf-chip">Commit</span>
                <span class="gf-chip">Push</span>
                <span class="gf-chip">Pull Request</span>
            </div>
        </div>
        <div style="width:1px;background:#30363d;"></div>
        <div style="flex:1;">
            <div style="font-weight:600;color:#e6edf3;margin-bottom:.3rem;">
                ⚙️ Part 2: GitHub Automation
            </div>
            <div style="font-size:.83rem;color:#8b949e;">
                GitHub Actions automatically executing workflows <em>in response to</em>
                push or PR events. These are <em>automated system responses</em>.
            </div>
            <div style="margin-top:.5rem;">
                <span class="gf-chip">GitHub Actions</span>
                <span class="gf-chip">Workflows</span>
                <span class="gf-chip">CI/CD</span>
                <span class="gf-chip">Webhooks</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab_git, tab_actions, tab_workflow, tab_webhooks, tab_foundations = st.tabs([
    "🌿 Git Operations",
    "⚙️ GitHub Actions",
    "🔁 CI/CD Pipeline",
    "🪝 Webhooks",
    "📚 GitHub Foundations",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — GIT OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_git:
    st.markdown("### 🌿 Git Operations Demo")
    st.markdown('<div style="font-size:.85rem;color:#8b949e;margin-bottom:1.5rem;">Demonstrates: creating branches, committing code, pushing to GitHub, and opening Pull Requests — the Git workflow used by the TeamSync development team.</div>', unsafe_allow_html=True)

    col_branch, col_ops = st.columns([1.8, 2.2])

    with col_branch:
        st.markdown("#### 🌿 Branch Strategy")
        branches = api_get("/api/github/branches", {"owner": "teamsync-demo", "repo": "online-exam-system"})
        if not branches:
            branches = [
                {"name":"main","protected":True},
                {"name":"develop","protected":False},
                {"name":"feature/authentication","protected":False},
                {"name":"feature/exam-module","protected":False},
                {"name":"feature/result-generation","protected":False},
                {"name":"bugfix/login-session","protected":False},
                {"name":"release/v1.0.0","protected":True},
            ]

        # Branch visualization
        st.markdown('<div class="git-graph">', unsafe_allow_html=True)

        for b in branches:
            is_protected = b.get("protected", False)
            name = b["name"]
            if name == "main":
                st.markdown(f'<div style="color:#3fb950;">● {name} <span style="color:#238636;font-size:.7rem;">[PROTECTED]</span></div>', unsafe_allow_html=True)
            elif name == "develop":
                st.markdown(f'<div style="color:#58a6ff;margin-left:1rem;">├─● {name}</div>', unsafe_allow_html=True)
            elif name.startswith("feature/"):
                feature = name.replace("feature/","")
                st.markdown(f'<div style="color:#bc6aff;margin-left:2rem;">│ ├─● feature/{feature}</div>', unsafe_allow_html=True)
            elif name.startswith("bugfix/"):
                st.markdown(f'<div style="color:#f85149;margin-left:2rem;">│ ├─● {name}</div>', unsafe_allow_html=True)
            elif name.startswith("release/"):
                st.markdown(f'<div style="color:#e3b341;margin-left:1rem;">├─● {name} <span style="color:#d29922;font-size:.7rem;">[PROTECTED]</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="color:#8b949e;margin-left:1rem;">├─● {name}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top:1rem;font-size:.78rem;color:#8b949e;">
            <div style="margin-bottom:.3rem;"><span style="color:#3fb950;">●</span> main — Production-ready, protected</div>
            <div style="margin-bottom:.3rem;"><span style="color:#58a6ff;">●</span> develop — Integration branch</div>
            <div style="margin-bottom:.3rem;"><span style="color:#bc6aff;">●</span> feature/* — New features</div>
            <div style="margin-bottom:.3rem;"><span style="color:#f85149;">●</span> bugfix/* — Bug fixes</div>
            <div><span style="color:#e3b341;">●</span> release/* — Release candidates</div>
        </div>
        """, unsafe_allow_html=True)

    with col_ops:
        st.markdown("#### 💻 Git Commands — Live Demo")

        ops = st.selectbox("Select Git Operation to Demonstrate", [
            "1. Clone Repository",
            "2. Create Feature Branch",
            "3. Stage & Commit Changes",
            "4. Push to GitHub",
            "5. Create Pull Request via GitHub CLI",
            "6. Merge Pull Request",
        ])

        terminal_outputs = {
            "1. Clone Repository": (
                "git clone https://github.com/teamsync-demo/online-exam-system.git",
                """<span class="t-gray">Cloning into 'online-exam-system'...</span>
<span class="t-gray">remote: Enumerating objects: 247, done.</span>
<span class="t-gray">remote: Counting objects: 100% (247/247), done.</span>
<span class="t-gray">remote: Compressing objects: 100% (163/163), done.</span>
<span class="t-green">✓</span> <span class="t-white">Receiving objects: 100% (247/247), 48.3 KiB | 2.1 MiB/s, done.</span>
<span class="t-green">✓</span> <span class="t-white">Repository cloned to: ./online-exam-system</span>""",
                "The repository is now available locally. All branches, commits, and history are downloaded.",
            ),
            "2. Create Feature Branch": (
                "git checkout -b feature/exam-timer\ngit branch",
                """<span class="t-green">✓</span> <span class="t-white">Switched to a new branch 'feature/exam-timer'</span>
<span class="t-gray">  develop</span>
<span class="t-gray">  feature/authentication</span>
<span class="t-green">* feature/exam-timer</span>   <span class="t-gray">← active branch</span>
<span class="t-gray">  main</span>""",
                "A new branch 'feature/exam-timer' was created and checked out. Changes here won't affect 'main' until a PR is merged.",
            ),
            "3. Stage & Commit Changes": (
                "git add backend/exam.py tests/test_exam.py\ngit status\ngit commit -m 'feat: Add exam timer with auto-submit'",
                """<span class="t-green">On branch feature/exam-timer</span>
<span class="t-white">Changes to be committed:</span>
<span class="t-green">	modified:   backend/exam.py</span>
<span class="t-green">	new file:   tests/test_exam.py</span>

<span class="t-green">[feature/exam-timer a1b2c3d]</span> <span class="t-white">feat: Add exam timer with auto-submit</span>
 <span class="t-gray">2 files changed, 87 insertions(+), 12 deletions(-)</span>""",
                "Files staged and committed with a meaningful commit message following conventional commits format.",
            ),
            "4. Push to GitHub": (
                "git push origin feature/exam-timer",
                """<span class="t-gray">Enumerating objects: 8, done.</span>
<span class="t-gray">Counting objects: 100% (8/8), done.</span>
<span class="t-gray">Delta compression using up to 8 threads</span>
<span class="t-gray">Compressing objects: 100% (5/5), done.</span>
<span class="t-gray">Writing objects: 100% (5/5), 2.84 KiB | 2.84 MiB/s, done.</span>
<span class="t-green">✓</span> <span class="t-white">Branch 'feature/exam-timer' pushed to 'origin'</span>
<span class="t-blue">remote: Create a pull request for 'feature/exam-timer' on GitHub:</span>
<span class="t-blue">remote:   https://github.com/teamsync-demo/online-exam-system/pull/new/feature/exam-timer</span>""",
                "Code is now on GitHub. GitHub Actions CI will automatically trigger when the PR is created.",
            ),
            "5. Create Pull Request via GitHub CLI": (
                "gh pr create --title 'feat: Add exam timer with auto-submit' \\\n  --body 'Implements #5 — countdown timer with auto-submit' \\\n  --base develop --head feature/exam-timer",
                """<span class="t-blue">Creating pull request for feature/exam-timer into develop in teamsync-demo/online-exam-system</span>

<span class="t-green">✓</span> <span class="t-white">Pull Request created: https://github.com/teamsync-demo/online-exam-system/pull/18</span>

<span class="t-gray">Title: feat: Add exam timer with auto-submit</span>
<span class="t-gray">Branch: feature/exam-timer → develop</span>
<span class="t-yellow">⚙ GitHub Actions CI triggered automatically...</span>
<span class="t-yellow">⚙ Running: TeamSync CI, Code Quality checks...</span>""",
                "The Pull Request is created on GitHub. CI/CD pipeline triggers automatically — this is where Git operations end and GitHub Automation begins.",
            ),
            "6. Merge Pull Request": (
                "gh pr merge 18 --merge --delete-branch",
                """<span class="t-gray">Merging pull request #18 (feat: Add exam timer with auto-submit)</span>
<span class="t-green">✓</span> <span class="t-white">Pull Request #18 merged into develop</span>
<span class="t-green">✓</span> <span class="t-white">Branch 'feature/exam-timer' deleted from remote</span>
<span class="t-yellow">⚙ GitHub Actions 'Deploy' workflow triggered on develop...</span>
<span class="t-blue">→ TeamSync dashboard updated: Task #3 linked to PR #18 marked as Completed</span>""",
                "PR merged. The feature branch is deleted. TeamSync updates the linked task status automatically via webhook.",
            ),
        }

        cmd, output, explanation = terminal_outputs[ops]

        st.markdown("**Command:**")
        st.code(cmd, language="bash")

        st.markdown("**Terminal Output:**")
        st.markdown(f'<div class="terminal">{output}</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:rgba(31,111,235,.06);border:1px solid rgba(31,111,235,.25);
            border-radius:8px;padding:.8rem 1rem;margin-top:.5rem;font-size:.83rem;color:#58a6ff;">
            💡 {explanation}
        </div>
        """, unsafe_allow_html=True)

    # Recent Commits
    st.markdown("---")
    st.markdown("#### 📦 Recent Commits (from GitHub API)")
    commits = api_get("/api/github/commits", {"owner": "teamsync-demo", "repo": "online-exam-system"})
    if not commits:
        commits = [
            {"sha":"a1b2c3d","commit":{"message":"feat: Add JWT authentication","author":{"name":"Arjun Mehta","date":"2024-11-28T14:00:00Z"}}},
            {"sha":"e4f5g6h","commit":{"message":"fix: Resolve session timeout bug","author":{"name":"Divya Reddy","date":"2024-11-28T10:00:00Z"}}},
            {"sha":"i7j8k9l","commit":{"message":"test: Add Pytest coverage for exam module","author":{"name":"Rohan Gupta","date":"2024-11-27T16:30:00Z"}}},
            {"sha":"m1n2o3p","commit":{"message":"ci: Update GitHub Actions workflow","author":{"name":"Arjun Mehta","date":"2024-11-27T09:00:00Z"}}},
            {"sha":"q4r5s6t","commit":{"message":"docs: Update README with setup guide","author":{"name":"Sneha Patel","date":"2024-11-26T17:00:00Z"}}},
        ]

    for c in commits[:6]:
        sha = c.get("sha","")[:7]
        msg = c.get("commit",{}).get("message","").split("\n")[0]
        author = c.get("commit",{}).get("author",{}).get("name","")
        date_str = c.get("commit",{}).get("author",{}).get("date","")[:10]

        # Detect commit type
        if msg.startswith("feat:"): msg_color = "#3fb950"
        elif msg.startswith("fix:"): msg_color = "#f85149"
        elif msg.startswith("test:"): msg_color = "#58a6ff"
        elif msg.startswith("ci:"): msg_color = "#e3b341"
        elif msg.startswith("docs:"): msg_color = "#8b949e"
        else: msg_color = "#e6edf3"

        st.markdown(f"""
        <div class="run-row">
            <span style="font-family:monospace;color:#bc6aff;font-size:.78rem;">⬡ {sha}</span>
            &nbsp;&nbsp;
            <span style="color:{msg_color};font-size:.85rem;">{msg}</span>
            <span style="float:right;font-size:.78rem;color:#8b949e;">👤 {author} · {date_str}</span>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — GITHUB ACTIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_actions:
    st.markdown("### ⚙️ GitHub Actions — Automated Workflows")
    st.markdown('<div style="font-size:.85rem;color:#8b949e;margin-bottom:1.5rem;">GitHub Actions automatically runs when a developer pushes code or opens a Pull Request. This is NOT a manual process — it is triggered by repository events.</div>', unsafe_allow_html=True)

    # How it triggers
    st.markdown("""
    <div style="background:rgba(35,134,54,.06);border:1px solid #238636;border-radius:10px;padding:1rem;margin-bottom:1.5rem;">
        <div style="font-weight:600;color:#3fb950;margin-bottom:.5rem;">🔔 How GitHub Actions Gets Triggered</div>
        <div style="display:flex;gap:2rem;font-size:.83rem;">
            <div>
                <div style="color:#e6edf3;font-weight:500;">Trigger 1: Push to branch</div>
                <code style="color:#8b949e;font-size:.78rem;">git push origin feature/exam-timer</code><br>
                <span style="color:#8b949e;">→ Actions runs on the pushed commit</span>
            </div>
            <div>
                <div style="color:#e6edf3;font-weight:500;">Trigger 2: Pull Request opened</div>
                <code style="color:#8b949e;font-size:.78rem;">gh pr create ...</code><br>
                <span style="color:#8b949e;">→ Actions validates code before merge</span>
            </div>
            <div>
                <div style="color:#e6edf3;font-weight:500;">Trigger 3: Merge to main</div>
                <code style="color:#8b949e;font-size:.78rem;">PR merged by reviewer</code><br>
                <span style="color:#8b949e;">→ Actions deploys to production</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_yaml, col_runs = st.columns([1.8, 2.2])

    with col_yaml:
        st.markdown("#### 📄 TeamSync CI Workflow (YAML)")
        st.code("""# .github/workflows/ci.yml
name: TeamSync CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  code-quality:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    steps:
      - name: ⬇️ Checkout Repository
        uses: actions/checkout@v4

      - name: 🐍 Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: 📦 Install Dependencies
        run: pip install -r requirements.txt

      - name: ⚡ Ruff Lint Check
        run: ruff check .

      - name: 🔒 Bandit Security Scan
        run: bandit -r backend -ll -ii

      - name: 🧪 Run Pytest
        run: pytest tests/ -v --cov=backend

      - name: 📊 Upload Coverage Report
        uses: codecov/codecov-action@v3""",
        language="yaml")

    with col_runs:
        st.markdown("#### 🏃 Recent Workflow Runs")

        runs_data = api_get("/api/github/workflow-runs", {"owner": "teamsync-demo", "repo": "online-exam-system"})
        workflow_runs = []
        if runs_data and isinstance(runs_data, dict):
            workflow_runs = runs_data.get("workflow_runs", [])

        if not workflow_runs:
            workflow_runs = [
                {"id":1005,"name":"Code Quality","status":"in_progress","conclusion":None,
                 "head_branch":"bugfix/login-session","event":"pull_request","run_number":43,
                 "created_at":"2024-11-28T15:30:00Z","html_url":"#"},
                {"id":1001,"name":"TeamSync CI","status":"completed","conclusion":"success",
                 "head_branch":"feature/authentication","event":"pull_request","run_number":42,
                 "created_at":"2024-11-28T14:00:00Z","html_url":"#"},
                {"id":1002,"name":"Code Quality","status":"completed","conclusion":"failure",
                 "head_branch":"feature/exam-module","event":"pull_request","run_number":41,
                 "created_at":"2024-11-28T10:30:00Z","html_url":"#"},
                {"id":1003,"name":"TeamSync CI","status":"completed","conclusion":"success",
                 "head_branch":"main","event":"push","run_number":40,
                 "created_at":"2024-11-27T18:00:00Z","html_url":"#"},
                {"id":1004,"name":"Deploy","status":"completed","conclusion":"success",
                 "head_branch":"main","event":"push","run_number":39,
                 "created_at":"2024-11-27T17:00:00Z","html_url":"#"},
            ]

        for run in workflow_runs:
            conclusion = run.get("conclusion")
            status = run.get("status")
            if status == "in_progress":
                icon, badge = "🟡", "badge-yellow"
                status_text = "Running..."
            elif conclusion == "success":
                icon, badge = "✅", "badge-green"
                status_text = "Passed"
            elif conclusion == "failure":
                icon, badge = "❌", "badge-red"
                status_text = "Failed"
            else:
                icon, badge = "⚪", "badge-gray"
                status_text = status

            event_badge = "badge-blue" if run.get("event") == "pull_request" else "badge-purple"
            event_text = "PR" if run.get("event") == "pull_request" else "Push"

            created = run.get("created_at","")[:16].replace("T"," ")
            branch = run.get("head_branch","")[:30]

            st.markdown(f"""
            <div class="run-row">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="font-size:1rem;">{icon}</span>
                        <strong style="color:#e6edf3;font-size:.88rem;margin-left:.3rem;">
                            {run['name']} #{run['run_number']}
                        </strong>
                        <span class="badge {event_badge}" style="margin-left:.5rem;font-size:.65rem;">{event_text}</span>
                    </div>
                    <span class="badge {badge}">{status_text}</span>
                </div>
                <div style="font-size:.77rem;color:#8b949e;margin-top:.3rem;">
                    🌿 {branch} &nbsp;·&nbsp; ⏰ {created}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Workflow jobs detail
    st.markdown("---")
    st.markdown("#### 🔍 Workflow Job Details — PR #13 (feature/exam-module) — ❌ Failed")

    job_steps = [
        ("✅", "⬇️ Checkout Repository", "success", "0s 8m", True),
        ("✅", "🐍 Setup Python 3.11", "success", "14s", True),
        ("✅", "📦 Install Dependencies", "success", "42s", True),
        ("❌", "⚡ Ruff Lint Check", "failure", "3s", True),
        ("⏭", "🔒 Bandit Security Scan", "skipped", "—", False),
        ("⏭", "🧪 Run Pytest", "skipped", "—", False),
    ]

    for icon, step_name, step_status, duration, completed in job_steps:
        step_class = "success-step" if step_status == "success" else "failure-step" if step_status == "failure" else "ci-step"
        st.markdown(f"""
        <div class="ci-step {step_class if step_status != 'skipped' else ''}">
            <span style="font-size:1.1rem;">{icon}</span>
            <span style="font-weight:500;font-size:.88rem;flex:1;color:{'#3fb950' if step_status=='success' else '#f85149' if step_status=='failure' else '#8b949e'};">
                {step_name}
            </span>
            <span style="font-size:.78rem;color:#8b949e;">{duration}</span>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📄 View Ruff Failure Log"):
        st.code("""Run ruff check .
backend/exam.py:12:1: F401 `os` imported but unused
  |
12 | import os
  | ^^^^^^^^^ F401
  |

backend/exam.py:45:80: E501 Line too long (92 > 88 characters)
  |
45 | return jsonify({"status": "error", "message": "The examination session has been invalidated"})
  |                                                                                ^^^^^^^^^^^^^^^^ E501
  |

backend/exam.py:78:5: F821 Undefined name `exam_service`
  |
78 |     result = exam_service.calculate_score(answers)
  |              ^^^^^^^^^^^^ F821
  |

backend/utils.py:23:1: I001 Import block is not sorted
  |
23 | import requests
24 | import os
25 | import flask
  | ^^^ I001
  |

Found 12 errors.
Error: Process completed with exit code 1.""", language="text")

    st.markdown("""
    <div style="background:rgba(218,54,51,.06);border:1px solid #da3633;border-radius:8px;
        padding:.8rem 1rem;margin-top:.5rem;font-size:.83rem;color:#f85149;">
        ❌ <strong>Workflow failed.</strong> Ruff found 12 linting issues. Subsequent steps (Bandit, Pytest) were skipped.
        The PR cannot be merged until these issues are fixed and CI passes.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CI/CD PIPELINE VISUALIZATION
# ══════════════════════════════════════════════════════════════════════════════
with tab_workflow:
    st.markdown("### 🔁 Complete CI/CD Pipeline")
    st.markdown('<div style="font-size:.85rem;color:#8b949e;margin-bottom:1.5rem;">End-to-end workflow from developer pushing code to production deployment. TeamSync monitors every stage.</div>', unsafe_allow_html=True)

    # Pipeline steps
    pipeline_scenarios = {
        "✅ PR #12 — feature/authentication (All Passed)": "success",
        "❌ PR #13 — feature/exam-module (Ruff Failed)": "failure",
        "⏳ PR #16 — feature/admin (In Progress)": "running",
    }

    selected_scenario = st.selectbox("Select Pipeline Run", list(pipeline_scenarios.keys()))
    scenario = pipeline_scenarios[selected_scenario]

    steps_config = {
        "success": [
            ("👨‍💻", "Developer", "git push", "Push to GitHub", "success", "Developer pushes feature branch"),
            ("🔔", "GitHub", "Event", "PR #12 Opened", "success", "GitHub detects new Pull Request"),
            ("⚙️", "Actions", "Trigger", "CI Workflow Started", "success", "GitHub Actions auto-triggered"),
            ("⚡", "Ruff", "Lint", "0 Issues Found", "success", "All code follows PEP 8 ✅"),
            ("🔒", "Bandit", "Security", "0 Vulnerabilities", "success", "No security issues found ✅"),
            ("🧪", "Pytest", "Tests", "42/42 Passed", "success", "Full test suite passed ✅"),
            ("👁️", "Reviewer", "Review", "PR Approved", "success", "Code review approved ✅"),
            ("🔀", "GitHub", "Merge", "Merged to main", "success", "PR safely merged ✅"),
            ("🚀", "Deploy", "CD", "Deployed", "success", "Live on production ✅"),
        ],
        "failure": [
            ("👨‍💻", "Developer", "git push", "Push to GitHub", "success", "Developer pushes feature branch"),
            ("🔔", "GitHub", "Event", "PR #13 Opened", "success", "GitHub detects new Pull Request"),
            ("⚙️", "Actions", "Trigger", "CI Workflow Started", "success", "GitHub Actions auto-triggered"),
            ("⚡", "Ruff", "Lint", "12 Issues Found", "failure", "Linting failed — unused imports, line length ❌"),
            ("🔒", "Bandit", "Security", "Skipped", "pending", "Skipped due to previous failure"),
            ("🧪", "Pytest", "Tests", "Skipped", "pending", "Skipped due to previous failure"),
            ("🚫", "GitHub", "Block", "Merge Blocked", "failure", "Cannot merge — CI checks must pass first ❌"),
            ("🔧", "Developer", "Fix", "Fix Linting Issues", "pending", "Developer must fix and re-push"),
            ("🔄", "Actions", "Re-run", "Re-run CI", "pending", "Waiting for fix..."),
        ],
        "running": [
            ("👨‍💻", "Developer", "git push", "Push to GitHub", "success", "Developer pushes feature branch"),
            ("🔔", "GitHub", "Event", "PR #16 Opened", "success", "GitHub detects new Pull Request"),
            ("⚙️", "Actions", "Trigger", "CI Workflow Started", "success", "GitHub Actions auto-triggered"),
            ("⚡", "Ruff", "Lint", "Running...", "running", "⏳ Checking code style..."),
            ("🔒", "Bandit", "Security", "Waiting", "pending", "Waiting for Ruff to complete"),
            ("🧪", "Pytest", "Tests", "Waiting", "pending", "Waiting for previous steps"),
            ("⏳", "GitHub", "Review", "Awaiting Review", "pending", "Reviewer assigned, waiting"),
            ("🔀", "GitHub", "Merge", "Blocked", "pending", "Cannot merge until CI completes"),
        ],
    }

    steps = steps_config[scenario]

    # Render pipeline
    pipeline_html = '<div style="display:flex;align-items:stretch;gap:.3rem;flex-wrap:wrap;margin:1rem 0;">'
    for i, (icon, actor, action, result, status, tooltip) in enumerate(steps):
        color = "#3fb950" if status=="success" else "#f85149" if status=="failure" else "#d29922" if status=="running" else "#30363d"
        bg = f"rgba({('35,134,54' if status=='success' else '218,54,51' if status=='failure' else '210,153,34' if status=='running' else '22,27,34')},.12)"
        status_text = "✅" if status=="success" else "❌" if status=="failure" else "🔄" if status=="running" else "⏳"

        pipeline_html += f"""
        <div style="flex:1;min-width:90px;background:{bg};border:1px solid {color};border-radius:8px;
            padding:.7rem .5rem;text-align:center;">
            <div style="font-size:1.3rem;">{icon}</div>
            <div style="font-size:.68rem;color:#8b949e;font-weight:600;text-transform:uppercase;margin:.2rem 0;">{actor}</div>
            <div style="font-size:.72rem;color:#e6edf3;font-weight:500;">{result[:15]}</div>
            <div style="font-size:1rem;margin-top:.3rem;">{status_text}</div>
        </div>
        """
        if i < len(steps) - 1:
            pipeline_html += '<div style="display:flex;align-items:center;color:#30363d;font-size:1.2rem;padding:0 .1rem;">→</div>'

    pipeline_html += "</div>"
    st.markdown(pipeline_html, unsafe_allow_html=True)

    # Detail table
    st.markdown("**Step Details:**")
    for icon, actor, action, result, status, tooltip in steps:
        status_badge = "badge-green" if status=="success" else "badge-red" if status=="failure" else "badge-yellow" if status=="running" else "badge-gray"
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding:.4rem .8rem;
            border-bottom:1px solid #21262d;font-size:.82rem;">
            <span style="width:30px;text-align:center;">{icon}</span>
            <span style="flex:1;color:#e6edf3;font-weight:500;">{result}</span>
            <span style="flex:2;color:#8b949e;">{tooltip}</span>
            <span class="badge {status_badge}">{status}</span>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — WEBHOOKS
# ══════════════════════════════════════════════════════════════════════════════
with tab_webhooks:
    st.markdown("### 🪝 GitHub Webhooks — Real-time Event Processing")
    st.markdown("""
    <div style="background:rgba(31,111,235,.06);border:1px solid #1f6feb;border-radius:10px;
        padding:1rem;margin-bottom:1.5rem;font-size:.83rem;">
        <strong style="color:#58a6ff;">What are Webhooks?</strong><br>
        <span style="color:#8b949e;">
        When something happens in a GitHub repository (PR opened, Issue created, push, etc.), GitHub sends an 
        HTTP POST request to your TeamSync backend URL. TeamSync processes this and updates the dashboard in real time —
        instead of polling the API repeatedly.
        </span>
    </div>
    """, unsafe_allow_html=True)

    col_config, col_events = st.columns([1.5, 2.5])

    with col_config:
        st.markdown("#### ⚙️ Webhook Configuration")
        st.markdown("""
        <div style="background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:1rem;font-size:.8rem;">
            <div style="color:#8b949e;margin-bottom:.5rem;">GitHub Repository → Settings → Webhooks</div>
            <div style="margin-bottom:.4rem;"><span style="color:#8b949e;">Payload URL:</span><br>
                <code style="color:#58a6ff;">https://teamsync.app/api/webhooks/github</code></div>
            <div style="margin-bottom:.4rem;"><span style="color:#8b949e;">Content type:</span>
                <code style="color:#3fb950;">application/json</code></div>
            <div style="margin-bottom:.4rem;"><span style="color:#8b949e;">Secret:</span>
                <code style="color:#e3b341;">••••••••••••</code></div>
            <div style="margin-bottom:.4rem;"><span style="color:#8b949e;">SSL Verification:</span>
                <span style="color:#3fb950;">Enabled ✅</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📋 Subscribed Events")
        events = [
            ("issues","Update Issue status in TeamSync"),
            ("pull_request","Sync PR status, review, merge"),
            ("pull_request_review","Update review status"),
            ("push","Log developer commits"),
            ("check_run","Update CI check results"),
            ("workflow_run","Update Actions pipeline status"),
            ("milestone","Sync milestone progress"),
        ]
        for evt, desc in events:
            st.markdown(f"""
            <div style="display:flex;gap:.5rem;margin-bottom:.3rem;font-size:.8rem;">
                <span style="color:#3fb950;">✓</span>
                <span style="color:#58a6ff;font-family:monospace;">{evt}</span>
                <span style="color:#8b949e;">— {desc}</span>
            </div>
            """, unsafe_allow_html=True)

    with col_events:
        st.markdown("#### 📨 Recent Webhook Events (Received by TeamSync)")

        webhook_events = [
            {
                "event":"pull_request","action":"opened","time":"15:34:22",
                "actor":"arjun-mehta","target":"PR #16: feat: Admin panel",
                "result":"PR synced to dashboard",
                "payload_preview":'"action":"opened","number":16,"pull_request":{"title":"feat: Admin panel...","state":"open"}'
            },
            {
                "event":"check_run","action":"completed","time":"15:33:10",
                "actor":"GitHub Actions","target":"Ruff check failed (PR #13)",
                "result":"Task linked to PR #13 flagged",
                "payload_preview":'"check_run":{"name":"Ruff","conclusion":"failure","status":"completed"}'
            },
            {
                "event":"pull_request_review","action":"submitted","time":"14:52:01",
                "actor":"priya-sharma","target":"PR #15 review: approved",
                "result":"PR #15 review_status → approved",
                "payload_preview":'"review":{"state":"APPROVED","user":{"login":"priya-sharma"}}'
            },
            {
                "event":"issues","action":"opened","time":"12:18:44",
                "actor":"rohan-gupta","target":"Issue #8: Login bug",
                "result":"Issue synced, is_bug=True",
                "payload_preview":'"issue":{"title":"Login button unresponsive","labels":[{"name":"bug"}]}'
            },
            {
                "event":"push","action":"pushed","time":"10:05:33",
                "actor":"divya-reddy","target":"feature/exam-module — 3 commits",
                "result":"Push logged",
                "payload_preview":'"ref":"refs/heads/feature/exam-module","commits":[...],"pusher":{"name":"divya-reddy"}'
            },
        ]

        for evt in webhook_events:
            event_color = {
                "pull_request":"#bc6aff","check_run":"#e3b341",
                "pull_request_review":"#3fb950","issues":"#f85149","push":"#58a6ff",
            }.get(evt["event"],"#8b949e")

            st.markdown(f"""
            <div class="webhook-event" style="border-left-color:{event_color};">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.3rem;">
                    <span style="color:{event_color};font-weight:600;">{evt['event']} · {evt['action']}</span>
                    <span style="color:#8b949e;font-size:.75rem;">{evt['time']}</span>
                </div>
                <div style="color:#8b949e;margin-bottom:.2rem;">
                    👤 {evt['actor']} → {evt['target']}
                </div>
                <div style="color:#3fb950;font-size:.75rem;">↳ {evt['result']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Security Note
    st.markdown("---")
    st.markdown("#### 🔒 Webhook Security")
    st.code("""# backend/services/sync_service.py
import hmac, hashlib

def verify_signature(self, payload_body: bytes, signature: str) -> bool:
    \"\"\"Verify X-Hub-Signature-256 to confirm webhook is from GitHub.\"\"\"
    secret = current_app.config.get("GITHUB_WEBHOOK_SECRET", "").encode()
    expected = "sha256=" + hmac.new(secret, payload_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")

# Also check delivery_id to prevent duplicate processing
existing = WebhookEvent.query.filter_by(delivery_id=delivery_id).first()
if existing and existing.processed:
    return {"status": "duplicate", "delivery_id": delivery_id}""", language="python")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — GITHUB FOUNDATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_foundations:
    st.markdown("### 📚 GitHub Foundations Concepts — Demonstrated in TeamSync")
    st.markdown('<div style="font-size:.85rem;color:#8b949e;margin-bottom:1.5rem;">This table shows exactly how each GitHub Foundations concept is demonstrated through the TeamSync project.</div>', unsafe_allow_html=True)

    concepts = [
        {
            "concept":"Repository",
            "icon":"📁",
            "where_used":"TeamSync connects to a GitHub repository via REST API.",
            "demo":"GitHub Repos page fetches real repo info, stars, forks, languages.",
            "api_endpoint":"GET /repos/{owner}/{repo}",
        },
        {
            "concept":"Branch",
            "icon":"🌿",
            "where_used":"Developers create feature branches for each task.",
            "demo":"Branch list shown in GitHub Repos page with protection status.",
            "api_endpoint":"GET /repos/{owner}/{repo}/branches",
        },
        {
            "concept":"Commit",
            "icon":"📦",
            "where_used":"Developers push commits to branches.",
            "demo":"Recent commits displayed with SHA, message, author, and date.",
            "api_endpoint":"GET /repos/{owner}/{repo}/commits",
        },
        {
            "concept":"Pull Request",
            "icon":"🔀",
            "where_used":"All code changes go through PRs before merging.",
            "demo":"PR page shows state, review status, CI checks, author, branch.",
            "api_endpoint":"GET /repos/{owner}/{repo}/pulls",
        },
        {
            "concept":"Issue",
            "icon":"🐛",
            "where_used":"Tasks and bugs are tracked as GitHub Issues.",
            "demo":"Issues page syncs from GitHub, classifies bugs, tracks resolution.",
            "api_endpoint":"GET /repos/{owner}/{repo}/issues",
        },
        {
            "concept":"Labels",
            "icon":"🏷️",
            "where_used":"Issues are categorized with labels (bug, enhancement, etc.)",
            "demo":"Label chips shown on each issue card. Bug detection uses 'bug' label.",
            "api_endpoint":"GET /repos/{owner}/{repo}/labels",
        },
        {
            "concept":"Milestones",
            "icon":"🏁",
            "where_used":"Project phases are tracked as GitHub Milestones.",
            "demo":"Dashboard shows milestone progress bars with % completion.",
            "api_endpoint":"GET /repos/{owner}/{repo}/milestones",
        },
        {
            "concept":"GitHub Actions",
            "icon":"⚙️",
            "where_used":"CI/CD runs automatically on every push and PR.",
            "demo":"Actions tab shows live workflow runs, job steps, pass/fail results.",
            "api_endpoint":"GET /repos/{owner}/{repo}/actions/runs",
        },
        {
            "concept":"Webhooks",
            "icon":"🪝",
            "where_used":"GitHub sends events to TeamSync backend in real time.",
            "demo":"Webhook tab shows received events, signature verification, processing.",
            "api_endpoint":"POST /api/webhooks/github (receives events)",
        },
        {
            "concept":"Collaborators",
            "icon":"👥",
            "where_used":"Team members are managed in project and GitHub.",
            "demo":"Team page shows GitHub usernames, roles, workload distribution.",
            "api_endpoint":"GET /repos/{owner}/{repo}/contributors",
        },
        {
            "concept":"README",
            "icon":"📄",
            "where_used":"Repository documentation and setup guide.",
            "demo":"README.md in the TeamSync repo documents architecture and usage.",
            "api_endpoint":"GET /repos/{owner}/{repo}/readme",
        },
        {
            "concept":"Permissions",
            "icon":"🔐",
            "where_used":"Role-based access (admin, developer, QA, viewer).",
            "demo":"TeamSync enforces roles — only leads can create projects, assign tasks.",
            "api_endpoint":"Role-based in TeamSync + GitHub repo permissions",
        },
    ]

    # Grid display
    cols_per_row = 3
    for i in range(0, len(concepts), cols_per_row):
        row_concepts = concepts[i:i+cols_per_row]
        cols = st.columns(cols_per_row)
        for col, c in zip(cols, row_concepts):
            with col:
                st.markdown(f"""
                <div class="concept-card">
                    <div class="concept-icon">{c['icon']}</div>
                    <div class="concept-title">{c['concept']}</div>
                    <div class="concept-desc">{c['where_used']}</div>
                    <div style="margin-top:.5rem;font-size:.78rem;color:#3fb950;">{c['demo']}</div>
                    <div style="margin-top:.5rem;background:#0d1117;border-radius:4px;padding:.3rem .5rem;">
                        <code style="font-size:.68rem;color:#bc6aff;">{c['api_endpoint']}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Summary table
    import pandas as pd
    st.markdown("#### 📋 Quick Reference Summary")
    df = pd.DataFrame([{
        "GitHub Concept": f"{c['icon']} {c['concept']}",
        "TeamSync Usage": c["where_used"],
        "Dashboard Location": c["demo"].split(".")[0],
    } for c in concepts])
    st.dataframe(df, use_container_width=True, hide_index=True)
