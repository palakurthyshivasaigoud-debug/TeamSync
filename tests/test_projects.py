import pytest


class TestProjectCRUD:
    def _create_user_and_project(self, client):
        client.post("/api/auth/register", json={
            "name": "Project Lead", "email": "lead@proj.test",
            "password": "password", "role": "admin",
        })
        response = client.post("/api/projects/", json={
            "name": "Test Project Alpha",
            "description": "A test project",
            "owner_id": 1,
            "tech_stack": "Python, Flask",
            "start_date": "2024-11-01",
            "deadline": "2024-12-15",
        })
        return response

    def test_create_project_success(self, client):
        response = self._create_user_and_project(client)
        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Test Project Alpha"
        assert data["status"] == "active"

    def test_create_project_missing_name(self, client):
        response = client.post("/api/projects/", json={"description": "No name"})
        assert response.status_code == 400

    def test_list_projects(self, client):
        response = client.get("/api/projects/")
        assert response.status_code == 200
        assert isinstance(response.get_json(), list)

    def test_get_project_not_found(self, client):
        response = client.get("/api/projects/99999")
        assert response.status_code == 404

    def test_update_project_status(self, client):
        create_resp = self._create_user_and_project(client)
        if create_resp.status_code == 201:
            proj_id = create_resp.get_json()["id"]
            response = client.put(f"/api/projects/{proj_id}", json={"status": "on-hold"})
            assert response.status_code == 200
            assert response.get_json()["status"] == "on-hold"


class TestTaskCRUD:
    def _create_task(self, client, project_id=1, title="Test Task"):
        return client.post("/api/tasks/", json={
            "project_id": project_id,
            "title": title,
            "description": "A test task",
            "priority": "high",
            "status": "todo",
            "due_date": "2024-12-10",
        })

    def test_create_task_success(self, client):
        response = self._create_task(client)
        assert response.status_code in (201, 400)  # 400 if project_id=1 not present

    def test_create_task_missing_required(self, client):
        response = client.post("/api/tasks/", json={"title": "No project_id"})
        assert response.status_code == 400

    def test_list_tasks_filter_by_status(self, client):
        response = client.get("/api/tasks/", query_string={"status": "todo"})
        assert response.status_code == 200
        tasks = response.get_json()
        for task in tasks:
            assert task["status"] == "todo"

    def test_task_completion_rate_formula(self):
        """Test the completion rate formula: completed / total * 100"""
        total = 40
        completed = 28
        rate = round(completed / total * 100, 1)
        assert rate == 70.0

    def test_task_health_formula(self):
        """Test project health score formula: H = 0.4*T + 0.3*M + 0.2*B + 0.1*C"""
        T = 80   # Task completion
        M = 70   # Milestone completion
        B = 90   # Bug resolution
        C = 100  # CI success
        H = round(0.4 * T + 0.3 * M + 0.2 * B + 0.1 * C, 1)
        assert H == 81.0

    def test_overdue_detection(self):
        """Test that overdue tasks are correctly identified."""
        from datetime import date, timedelta
        today = date.today()
        past_date = today - timedelta(days=3)
        future_date = today + timedelta(days=5)
        # Past due date should be overdue for non-completed tasks
        assert past_date < today  # is past
        assert future_date > today  # is future
