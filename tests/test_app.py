"""
Tests for the High School Management System API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that the response contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Basketball" in activities


class TestSignUpForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "signed up" in response.json()["message"].lower()
    
    def test_signup_adds_participant(self, client):
        """Test that signup adds the participant to the activity"""
        email = "student@mergington.edu"
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_email_returns_400(self, client):
        """Test that signing up with duplicate email returns 400"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    """Test the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregister from an activity"""
        # First sign up
        email = "tempstudent@mergington.edu"
        client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        # Then unregister
        response = client.delete(
            "/activities/Tennis Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "unregistered" in response.json()["message"].lower()
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister removes the participant from the activity"""
        email = "tempstudent2@mergington.edu"
        # First sign up
        client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        # Then unregister
        client.delete(
            "/activities/Drama Club/unregister",
            params={"email": email}
        )
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Drama Club"]["participants"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_not_signed_up_returns_400(self, client):
        """Test that unregistering when not signed up returns 400"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()


class TestRootEndpoint:
    """Test the root GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
