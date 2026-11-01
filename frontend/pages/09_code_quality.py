import streamlit as st
import requests

BACKEND = "http://localhost:5000"
st.set_page_config(page_title="Code Quality — TeamSync", page_icon="🛡️", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif!important;}
.stApp{background:linear-gradient(135deg,#0d1117,#161b22,#0d1117);color:#e6edf3;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#161b22,#0d1117);border-right:1px solid #30363d;}
.ts-card{background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem;}
.tool-card{background:rgba(22,27,34,.9);border:1px solid #30363d;border-radius:12px;padding:1.3rem;
  text-align:center;transition:all .2s;}
.tool-card:hover{border-color:#58a6ff;transform:translateY(-2px);}
.report-row{background:rgba(13,17,23,.6);border:1px solid #21262d;border-radius:8px;
  padding:.8rem 1rem;margin-bottom:.4rem;}
.badge{display:inline-block;padding:.2rem .6rem;border-radius:20px;font-size:.72rem;font-weight:600;text-transform:uppercase;}
.badge-green{background:rgba(35,134,54,.2);color:#3fb950;border:1px solid #238636;}
.badge-red{background:rgba(218,54,51,.2);color:#f85149;border:1px solid #da3633;}
.badge-yellow{background:rgba(210,153,34,.2);color:#e3b341;border:1px solid #d29922;}
.badge-gray{background:rgba(110,118,129,.2);color:#8b949e;border:1px solid #6e7681;}
.code-block{background:#0d1117;border:1px solid #30363d;border-radius:8px;
  padding:1rem;font-family:monospace;font-size:.8rem;color:#e6edf3;margin:.5rem 0;overflow-x:auto;}
.ai-explain{background:linear-gradient(135deg,rgba(188,106,255,.06),rgba(31,111,235,.06));
  border:1px solid rgba(188,106,255,.3);border-radius:10px;padding:1rem;}
</style>""", unsafe_allow_html=True)


def api_get(p, params=None):
    try: return requests.get(f"{BACKEND}{p}", params=params, timeout=8).json()
    except: return None


TOOL_INFO = {
    "ruff":    {"icon":"⚡","name":"Ruff","desc":"Python linter & formatter (PEP 8)","color":"#58a6ff"},
    "bandit":  {"icon":"🔒","name":"Bandit","desc":"Python security vulnerability scanner","color":"#e3b341"},
    "pytest":  {"icon":"🧪","name":"Pytest","desc":"Automated unit & integration testing","color":"#3fb950"},
    "github_actions":{"icon":"⚙️","name":"GitHub Actions","desc":"CI/CD pipeline automation","color":"#bc6aff"},
}
STATUS_BADGE = {"passed":"badge-green","failed":"badge-red","pending":"badge-yellow","skipped":"badge-gray"}

st.markdown("""
<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid #21262d;margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:700;color:#e6edf3;">🛡️ Code Quality</div>
  <div style="font-size:.9rem;color:#8b949e;">Ruff · Bandit · Pytest · GitHub Actions CI results</div>
</div>
""", unsafe_allow_html=True)

tab_reports, tab_tools, tab_ai = st.tabs(["📋 Quality Reports", "🛠️ Tools Overview", "🤖 AI Explanations"])

with tab_reports:
    reports = api_get("/api/quality/1")
    summary = api_get("/api/quality/summary/1")

    if summary:
        pass_rate = summary.get("overall_pass_rate", 0)
        by_tool = summary.get("by_tool", {})

        col_sum = st.columns(1 + len(by_tool))
        with col_sum[0]:
            color = "#3fb950" if pass_rate >= 80 else "#e3b341" if pass_rate >= 50 else "#f85149"
            st.markdown(f"""
            <div class="tool-card" style="border-color:{color};">
                <div style="font-size:2rem;">🏆</div>
                <div style="font-size:2rem;font-weight:800;color:{color};">{pass_rate}%</div>
                <div style="font-size:.75rem;color:#8b949e;">OVERALL PASS RATE</div>
            </div>
            """, unsafe_allow_html=True)

        for col, (tool, data) in zip(col_sum[1:], by_tool.items()):
            info = TOOL_INFO.get(tool, {"icon":"🔧","name":tool,"color":"#58a6ff"})
            passed = data.get("passed",0)
            total = data.get("total",0)
            rate = round(passed/total*100, 0) if total > 0 else 0
            color = "#3fb950" if rate >= 80 else "#e3b341" if rate >= 50 else "#f85149"
            with col:
                st.markdown(f"""
                <div class="tool-card">
                    <div style="font-size:1.5rem;">{info['icon']}</div>
                    <div style="font-size:.85rem;font-weight:700;color:{info['color']};">{info['name']}</div>
                    <div style="font-size:1.5rem;font-weight:800;color:{color};">{rate:.0f}%</div>
                    <div style="font-size:.7rem;color:#8b949e;">{passed}/{total} passed</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if reports:
        # Group by PR
        prs_seen = set()
        for r in reports:
            prs_seen.add(r.get("github_pr_number"))

        for pr_num in sorted(prs_seen, reverse=True):
            pr_reports = [r for r in reports if r.get("github_pr_number") == pr_num]
            all_passed = all(r["status"] == "passed" for r in pr_reports)
            any_failed = any(r["status"] == "failed" for r in pr_reports)
            pr_status = "✅ All Passed" if all_passed else "❌ Failed" if any_failed else "⏳ Pending"
            pr_color = "#3fb950" if all_passed else "#f85149" if any_failed else "#e3b341"

            with st.expander(f"🔀 PR #{pr_num} — {pr_status}", expanded=any_failed):
                for r in pr_reports:
                    info = TOOL_INFO.get(r["tool_name"], {"icon":"🔧","name":r["tool_name"],"color":"#58a6ff"})
                    status_badge = STATUS_BADGE.get(r["status"], "badge-gray")
                    issues_text = f"· {r['issues_found']} issues found" if r.get("issues_found") else ""

                    st.markdown(f"""
                    <div class="report-row">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <span style="font-size:1.1rem;">{info['icon']}</span>
                                <strong style="color:{info['color']};margin-left:.4rem;">{info['name']}</strong>
                                <span style="color:#8b949e;font-size:.82rem;margin-left:.4rem;">{issues_text}</span>
                            </div>
                            <span class="badge {status_badge}">{r['status']}</span>
                        </div>
                        <div style="font-size:.82rem;color:#8b949e;margin-top:.3rem;">{r.get('summary','')}</div>
                    </div>
                    """, unsafe_allow_html=True)

with tab_tools:
    st.markdown("#### 🛠️ Code Quality Tools")

    for tool_key, info in TOOL_INFO.items():
        with st.expander(f"{info['icon']} {info['name']} — {info['desc']}", expanded=False):
            cols = st.columns([2, 1.5])
            with cols[0]:
                tool_configs = {
                    "ruff": {
                        "purpose": "Python linting, PEP 8 compliance, code formatting",
                        "config": """# pyproject.toml
[tool.ruff]
line-length = 88
select = ["E", "W", "F", "I", "N"]
ignore = ["E501"]
exclude = ["migrations/", ".venv/"]""",
                        "command": "ruff check . --fix",
                    },
                    "bandit": {
                        "purpose": "Detect common Python security vulnerabilities",
                        "config": """# .bandit
[bandit]
targets = backend
exclude = tests, .venv
level = MEDIUM""",
                        "command": "bandit -r backend -ll -ii",
                    },
                    "pytest": {
                        "purpose": "Automated unit and integration testing",
                        "config": """# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --cov=backend --cov-report=term-missing""",
                        "command": "pytest tests/ -v --cov=backend",
                    },
                    "github_actions": {
                        "purpose": "Automate CI/CD workflows on push/PR",
                        "config": """# .github/workflows/ci.yml
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest""",
                        "command": "Triggered automatically by GitHub",
                    },
                }
                cfg = tool_configs.get(tool_key, {})
                st.markdown(f"**Purpose:** {cfg.get('purpose','')}")
                st.code(cfg.get("config",""), language="toml")
            with cols[1]:
                st.markdown("**Run Command:**")
                st.code(cfg.get("command",""), language="bash")

with tab_ai:
    st.markdown("#### 🤖 AI-Assisted Code Quality Explanations")
    st.markdown("""
    <div style="background:rgba(188,106,255,.06);border:1px solid rgba(188,106,255,.3);border-radius:10px;
        padding:1rem;margin-bottom:1rem;font-size:.85rem;color:#bc6aff;">
        <strong>Note:</strong> AI explanations are generated using GitHub Copilot assistance during development.
        TeamSync retrieves actual check results from GitHub Actions and presents them with structured guidance.
    </div>
    """, unsafe_allow_html=True)

    # Example failed check with AI explanation
    examples = [
        {
            "pr": 13,
            "tool": "pytest",
            "status": "failed",
            "error": """FAILED tests/test_exam.py::test_exam_submit - AssertionError
FAILED tests/test_exam.py::test_result_calc - ZeroDivisionError  
FAILED tests/test_exam.py::test_timer_auto_submit - TimeoutError""",
            "ai_explanation": """🔍 **Root Cause Analysis:**

**test_exam_submit** — The `submit_exam()` function fails an assertion check.
The test expects `response.status_code == 200` but receives `422 Unprocessable Entity`.
This usually means the request payload is missing required fields.

**test_result_calc** — `ZeroDivisionError` in `calculate_percentage()`.
The function divides `correct_answers / total_questions` without checking if `total_questions == 0`.

**test_timer_auto_submit** — `TimeoutError` suggests the auto-submit timer isn't being triggered
within the 5-second test window. The timer callback may not be properly registered.

✅ **Suggested Fixes:**
1. Add payload validation before calling `submit_exam()`
2. Add guard clause: `if total_questions == 0: return 0`
3. Use `asyncio.wait_for()` or mock the timer in tests""",
        },
        {
            "pr": 13,
            "tool": "ruff",
            "status": "failed",
            "error": """backend/exam.py:12:1: F401 `os` imported but unused
backend/exam.py:45:80: E501 line too long (92 > 88 characters)
backend/exam.py:78:5: F821 undefined name 'exam_service'
backend/utils.py:23:1: I001 import block not sorted""",
            "ai_explanation": """🔍 **Linting Issues Found:**

**F401 (Unused import)** — `import os` on line 12 is not used anywhere in the file.
Remove it to keep the codebase clean.

**E501 (Line too long)** — Line 45 exceeds the 88-character limit.
Break the long expression into multiple lines.

**F821 (Undefined name)** — `exam_service` is referenced on line 78 but never defined.
You likely forgot to import it: `from services.exam_service import exam_service`

**I001 (Unsorted imports)** — Use `ruff check . --fix` to auto-sort imports.""",
        },
    ]

    for ex in examples:
        info = TOOL_INFO.get(ex["tool"], {"icon":"🔧","name":ex["tool"],"color":"#58a6ff"})
        s_badge = "badge-red" if ex["status"] == "failed" else "badge-green"
        with st.expander(f"PR #{ex['pr']} · {info['icon']} {info['name']} · ❌ Failed — Click for AI Explanation"):
            st.markdown("**🔴 Error Output:**")
            st.code(ex["error"], language="text")
            st.markdown(f"""
            <div class="ai-explain">
                <div style="font-size:.8rem;color:#bc6aff;font-weight:600;margin-bottom:.5rem;">
                    🤖 AI-Assisted Explanation (GitHub Copilot)
                </div>
                <div style="font-size:.85rem;color:#e6edf3;">{ex['ai_explanation'].replace(chr(10),'<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
