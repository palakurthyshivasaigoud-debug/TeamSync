# 🔗 TeamSync AI — GitHub-Based Team Project Management

> **Industry Track PBL Project** | GitHub Foundations + AI-Assisted Code Quality

TeamSync is a GitHub-integrated team project management platform that helps software development teams plan projects, assign tasks, monitor deadlines, track bugs, manage Pull Requests, and evaluate overall progress through a unified dashboard.

---

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/your-org/teamsync.git
cd teamsync
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GITHUB_TOKEN
```

### 3. Run the Backend (Flask API)

```bash
python run_backend.py
# → Runs on http://localhost:5000
# → Auto-creates SQLite DB and seeds demo data on first run
```

### 4. Run the Frontend (Streamlit Dashboard)

```bash
streamlit run frontend/app.py
# → Opens at http://localhost:8501
```

> **Login credentials (demo):**
> - Email: `priya@teamsync.dev` | Password: `password123` (Admin/Lead)
> - Email: `arjun@teamsync.dev` | Password: `password123` (Developer)

---

## 🏗️ Project Structure

```
TeamSync/
├── backend/                    # Flask REST API
│   ├── __init__.py             # App factory + demo seeder
│   ├── config.py               # Configuration
│   ├── extensions.py           # Flask extensions (db, bcrypt, login)
│   ├── models.py               # SQLAlchemy models
│   ├── routes/                 # API Blueprints
│   │   ├── auth.py             # /api/auth/* — Login, register
│   │   ├── projects.py         # /api/projects/* — CRUD
│   │   ├── tasks.py            # /api/tasks/* — Task management
│   │   ├── github.py           # /api/github/* — GitHub API proxy
│   │   ├── analytics.py        # /api/analytics/* — Metrics
│   │   ├── team.py             # /api/team/* — Team management
│   │   ├── quality.py          # /api/quality/* — Code quality reports
│   │   └── webhooks.py         # /api/webhooks/* — GitHub webhooks
│   └── services/               # Business logic
│       ├── github_service.py   # GitHub REST API integration
│       ├── analytics_service.py# Project health & productivity analytics
│       └── sync_service.py     # GitHub ↔ Database synchronization
├── frontend/                   # Streamlit Dashboard
│   ├── app.py                  # Entry point, login, navigation
│   └── pages/                  # Multi-page app
│       ├── 01_dashboard.py     # Project health overview
│       ├── 02_projects.py      # Project management
│       ├── 03_tasks.py         # Kanban task board
│       ├── 04_github_repos.py  # Repository explorer
│       ├── 05_pull_requests.py # PR monitoring
│       ├── 06_issues_bugs.py   # Issue & bug tracker
│       ├── 07_team.py          # Team management
│       ├── 08_analytics.py     # Developer productivity analytics
│       ├── 09_code_quality.py  # Ruff, Bandit, Pytest reports
│       ├── 10_github_devops.py # GitHub DevOps & Automation demo
│       └── 11_notifications.py # Alerts & notifications
├── tests/                      # Pytest test suite
│   ├── conftest.py             # Flask test fixtures
│   ├── test_auth.py            # Authentication tests
│   └── test_projects.py        # Project & task tests
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── requirements.txt
├── run_backend.py
└── .env.example
```

---

## 📊 Technology Stack

| Component | Technology |
|---|---|
| Frontend / Dashboard | Streamlit |
| Backend | Python + Flask |
| Database | SQLite (Flask-SQLAlchemy) |
| GitHub Integration | GitHub REST API (PyGithub) |
| Code Quality | Ruff, Bandit |
| Testing | Pytest + pytest-cov |
| CI/CD | GitHub Actions |
| Version Control | Git & GitHub |
| AI Dev Support | GitHub Copilot |

---

## 🔢 Project Health Formula

$$H = 0.4 \times T + 0.3 \times M + 0.2 \times B + 0.1 \times C$$

| Variable | Meaning |
|---|---|
| T | Task completion rate (%) |
| M | Milestone completion rate (%) |
| B | Bug resolution rate (%) |
| C | CI/CD success rate (%) |

---

## 🤖 GitHub Actions CI Pipeline

The `.github/workflows/ci.yml` pipeline runs on every `push` and `pull_request`:

1. **Ruff** — PEP 8 linting and import checks
2. **Bandit** — Security vulnerability scanning
3. **Pytest** — Full test suite with coverage report
4. **pip-audit** — Dependency CVE scanning

---

## 👥 Team Roles (Demo Data)

| Name | Email | Role |
|---|---|---|
| Priya Sharma | priya@teamsync.dev | Admin / Team Lead |
| Arjun Mehta | arjun@teamsync.dev | Developer |
| Divya Reddy | divya@teamsync.dev | Developer |
| Rohan Gupta | rohan@teamsync.dev | QA Engineer |
| Sneha Patel | sneha@teamsync.dev | Developer |

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/auth/login` | POST | User login |
| `/api/auth/register` | POST | User registration |
| `/api/projects/` | GET / POST | List / create projects |
| `/api/projects/<id>` | GET / PUT / DELETE | Project detail |
| `/api/tasks/` | GET / POST | List / create tasks |
| `/api/tasks/<id>` | PUT | Update task status |
| `/api/analytics/overview` | GET | Project health metrics |
| `/api/analytics/workload` | GET | Developer workload |
| `/api/analytics/weekly` | GET | Weekly activity trend |
| `/api/github/repos` | GET | GitHub repositories |
| `/api/github/issues` | GET | GitHub issues |
| `/api/github/pull-requests` | GET | GitHub pull requests |
| `/api/quality/reports` | GET | Code quality reports |
| `/api/team/members` | GET | Team members |
| `/api/webhooks/github` | POST | GitHub webhook receiver |

---

## 🎓 GitHub Foundations Concepts Demonstrated

| Concept | Where Demonstrated |
|---|---|
| Repositories | GitHub Repos page — connect, view, sync |
| Branches | Branch strategy on DevOps page |
| Commits | Recent commits view in Repos page |
| Pull Requests | PR monitoring dashboard |
| Issues | Issue & Bug tracker |
| Labels & Milestones | Issues page, milestone tracking |
| GitHub Actions | CI pipeline + DevOps page live demo |
| Webhooks | Webhook event log on DevOps page |
| GitHub API | Live data sync from GitHub REST API |
| Fork & Clone | Documented in DevOps page workflow |

