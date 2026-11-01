import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Set MPLCONFIGDIR
os.environ['MPLCONFIGDIR'] = os.path.join(os.environ.get('TEMP', '.'), 'mpl_cache')

output_dir = r"C:\Users\palak\.gemini\antigravity\brain\8f80f6e1-b740-4753-9daa-e0e501459fac"
os.makedirs(output_dir, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 1.0

# -------------------------------------------------------------
# Figure 1: Health Score Breakdown & Metric Analysis
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), dpi=300)

# Donut chart for weights
weights = [40, 30, 20, 10]
labels = ['Task Completion (40%)', 'Milestone Progress (30%)', 'Bug Resolution (20%)', 'CI/CD Pass Rate (10%)']
colors = ['#0284c7', '#0ea5e9', '#f59e0b', '#10b981']

wedges, texts, autotexts = ax1.pie(
    weights, labels=labels, autopct='%1.0f%%', startangle=140,
    colors=colors, pctdistance=0.75,
    textprops={'fontsize': 9, 'color': '#0f172a', 'weight': 'bold'},
    wedgeprops={'width': 0.45, 'edgecolor': 'white', 'linewidth': 2}
)
for at in autotexts:
    at.set_color('white')
ax1.set_title("A. Dynamic Health Formula Weights", fontsize=11, fontweight='bold', pad=12, color='#0f172a')

# Bar chart for live metric performance
metrics = ['Task Comp. (T)', 'Milestone (M)', 'Bug Res. (B)', 'CI Rate (C)', 'Final Health (H)']
scores = [25.0, 24.4, 62.5, 88.0, 29.0]
bar_colors = ['#38bdf8', '#38bdf8', '#fbbf24', '#34d399', '#6366f1']

bars = ax2.bar(metrics, scores, color=bar_colors, width=0.55, edgecolor='#cbd5e1', linewidth=1)
ax2.set_ylim(0, 100)
ax2.set_ylabel("Performance (%)", fontsize=10, fontweight='bold', color='#334155')
ax2.set_title("B. Current Live Project Telemetry Scores", fontsize=11, fontweight='bold', pad=12, color='#0f172a')
ax2.grid(axis='y', linestyle='--', alpha=0.6)

for bar in bars:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f"{yval:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#0f172a')

plt.tight_layout()
fig1_path = os.path.join(output_dir, "figure1_health_score_breakdown.png")
fig.savefig(fig1_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved:", fig1_path)

# -------------------------------------------------------------
# Figure 2: Developer Workload & Sprint Velocity
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2), dpi=300)

# Workload stacked bar chart
devs = ['Arjun M.', 'Sneha P.', 'Divya R.', 'Rohan G.', 'Priya S.']
completed = np.array([3, 0, 0, 0, 0])
in_prog = np.array([1, 0, 2, 0, 0])
in_review = np.array([0, 0, 0, 1, 0])
todo_blocked = np.array([0, 4, 1, 0, 0])

p1 = ax1.bar(devs, completed, label='Completed', color='#10b981', width=0.5)
p2 = ax1.bar(devs, in_prog, bottom=completed, label='In Progress', color='#3b82f6', width=0.5)
p3 = ax1.bar(devs, in_review, bottom=completed+in_prog, label='In Review', color='#f59e0b', width=0.5)
p4 = ax1.bar(devs, todo_blocked, bottom=completed+in_prog+in_review, label='To Do / Blocked', color='#94a3b8', width=0.5)

ax1.set_ylabel("Number of Assigned Tasks", fontsize=10, fontweight='bold', color='#334155')
ax1.set_title("A. Team Member Workload Allocation", fontsize=11, fontweight='bold', pad=12, color='#0f172a')
ax1.set_ylim(0, 6)
ax1.legend(loc='upper right', frameon=True, fontsize=8)
ax1.grid(axis='y', linestyle='--', alpha=0.6)

# Sprint velocity / burndown trajectory
weeks = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8 (Now)']
ideal_burndown = [12, 10.5, 9.0, 7.5, 6.0, 4.5, 3.0, 1.5]
actual_remaining = [12, 12, 11, 10, 10, 9, 9, 9]

ax2.plot(weeks, ideal_burndown, marker='o', linestyle='--', color='#94a3b8', label='Ideal Burndown Target', linewidth=2)
ax2.plot(weeks, actual_remaining, marker='s', linestyle='-', color='#ef4444', label='Actual Remaining Work', linewidth=2.5)
ax2.set_ylabel("Remaining Unresolved Tasks", fontsize=10, fontweight='bold', color='#334155')
ax2.set_title("B. Sprint Burndown Trajectory (16 Days Left)", fontsize=11, fontweight='bold', pad=12, color='#0f172a')
ax2.set_ylim(0, 14)
ax2.legend(loc='upper right', frameon=True, fontsize=8)
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
fig2_path = os.path.join(output_dir, "figure2_workload_and_sprint_velocity.png")
fig.savefig(fig2_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved:", fig2_path)

# -------------------------------------------------------------
# Figure 3: Code Quality, CI Telemetry & Defect Taxonomy
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.0), dpi=300)

# Tool diagnostics summary
tools = ['Ruff Linter\n(Style/PEP8)', 'Bandit Security\n(AST Audit)', 'Pytest Suite\n(Unit Tests)']
passed_runs = [4, 3, 2]
failed_runs = [1, 0, 2]

x = np.arange(len(tools))
width = 0.35

rects1 = ax1.bar(x - width/2, passed_runs, width, label='Passing Runs', color='#10b981', edgecolor='#cbd5e1')
rects2 = ax1.bar(x + width/2, failed_runs, width, label='Failed Runs / Diagnostics', color='#ef4444', edgecolor='#cbd5e1')

ax1.set_ylabel("Recorded Report Counts", fontsize=10, fontweight='bold', color='#334155')
ax1.set_title("A. Automated Tool Execution Summary (9 Total)", fontsize=11, fontweight='bold', pad=12, color='#0f172a')
ax1.set_xticks(x)
ax1.set_xticklabels(tools, fontsize=9)
ax1.legend(loc='upper right', frameon=True, fontsize=8)
ax1.grid(axis='y', linestyle='--', alpha=0.6)

# Defect Taxonomy Bar
categories = ['Auth Token', 'Auto-Submit', 'Pool Exhaustion', 'Pagination', 'PDF Export', 'Session Timeout', 'Responsive UI', 'Docs Badge']
states = ['Open', 'Open', 'Open', 'Closed', 'Open', 'Open', 'Closed', 'Closed']
severity = ['Critical Bug', 'Feature', 'High Bug', 'Feature', 'Feature', 'Security Bug', 'UI Bug', 'Docs']
colors_cat = ['#ef4444' if 'Bug' in s else '#3b82f6' for s in severity]

y_pos = np.arange(len(categories))
ax2.barh(y_pos, [1]*len(categories), color=colors_cat, height=0.6, edgecolor='#cbd5e1')
ax2.set_yticks(y_pos)
ax2.set_yticklabels([f"#{i+1} {categories[i]} ({states[i]})" for i in range(len(categories))], fontsize=8.5)
ax2.set_xlabel("Classification (Red: Defect, Blue: Enhancement)", fontsize=9, fontweight='bold', color='#334155')
ax2.set_title("B. GitHub Issues & Defect Registry (8 Items)", fontsize=11, fontweight='bold', pad=12, color='#0f172a')
ax2.set_xlim(0, 1.2)
ax2.xaxis.set_visible(False)
ax2.grid(False)

plt.tight_layout()
fig3_path = os.path.join(output_dir, "figure3_code_quality_and_ci_telemetry.png")
fig.savefig(fig3_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved:", fig3_path)

# -------------------------------------------------------------
# Figure 4: System Architecture & Workflow Pipeline
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 4.8), dpi=300)
ax.axis('off')

# Draw architecture boxes
boxes = [
    {"label": "1. Client & Presentation Layer\nStreamlit Dashboard (Port 8501)\nHigh-Density Light Theme · Personas & Tabs", "x": 0.05, "y": 0.65, "w": 0.40, "h": 0.26, "color": "#e0f2fe", "border": "#0284c7"},
    {"label": "2. Application & API Layer\nFlask REST API (Port 5000)\nModular Blueprints · Auth · Sync Service", "x": 0.55, "y": 0.65, "w": 0.40, "h": 0.26, "color": "#f1f5f9", "border": "#475569"},
    {"label": "3. Persistence & Relational Layer\nSQLite Database (teamsync.db)\n8 Relational Models · SQLAlchemy ORM", "x": 0.05, "y": 0.15, "w": 0.40, "h": 0.26, "color": "#fef3c7", "border": "#d97706"},
    {"label": "4. External VCS & Automation Layer\nGitHub REST API & Actions CI/CD\nPytest (19/19) · Ruff · Bandit · Webhooks", "x": 0.55, "y": 0.15, "w": 0.40, "h": 0.26, "color": "#dcfce7", "border": "#16a34a"},
]

for b in boxes:
    rect = plt.Rectangle((b["x"], b["y"]), b["w"], b["h"], facecolor=b["color"], edgecolor=b["border"], linewidth=2, linestyle='-', transform=ax.transAxes, zorder=2)
    ax.add_patch(rect)
    ax.text(b["x"] + b["w"]/2, b["y"] + b["h"]/2, b["label"], ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0f172a', transform=ax.transAxes, zorder=3)

# Connectors
ax.annotate("", xy=(0.54, 0.78), xytext=(0.46, 0.78), arrowprops=dict(arrowstyle="<->", color="#0284c7", lw=2.5), zorder=4)
ax.annotate("", xy=(0.25, 0.42), xytext=(0.25, 0.64), arrowprops=dict(arrowstyle="<->", color="#475569", lw=2.5), zorder=4)
ax.annotate("", xy=(0.75, 0.42), xytext=(0.75, 0.64), arrowprops=dict(arrowstyle="<->", color="#16a34a", lw=2.5), zorder=4)
ax.annotate("", xy=(0.54, 0.28), xytext=(0.46, 0.28), arrowprops=dict(arrowstyle="<->", color="#d97706", lw=2.5), zorder=4)

ax.set_title("TeamSync End-to-End System Architecture & Layered Communication", fontsize=12, fontweight='bold', pad=15, color='#0f172a')

fig4_path = os.path.join(output_dir, "figure4_system_architecture.png")
fig.savefig(fig4_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved:", fig4_path)

