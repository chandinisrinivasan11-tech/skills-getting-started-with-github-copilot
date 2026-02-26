"""
FastAPI tests using AAA (Arrange-Act-Assert) pattern
"""
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_redirects_to_static(self):
        """Arrange: client ready; Act: GET /; Assert: redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test retrieving all activities"""

    def test_get_activities_returns_dict(self):
        """Arrange: activities initialized; Act: GET /activities; Assert: returns dict"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)

    def test_get_activities_has_chess_club(self):
        """Arrange: activities initialized; Act: GET /activities; Assert: contains Chess Club"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities

    def test_activity_has_required_fields(self):
        """Arrange: activities initialized; Act: GET /activities; Assert: each activity has schema"""
        response = client.get("/activities")
        activities = response.json()
        activity = activities["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignupForActivity:
    """Test signing up for an activity"""

    def test_signup_with_valid_activity_and_email(self):
        """Arrange: valid activity name and email; Act: POST signup; Assert: success"""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newtest@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newtest@mergington.edu" in data["message"]

    def test_signup_with_nonexistent_activity(self):
        """Arrange: invalid activity name; Act: POST signup; Assert: 404 error"""
        response = client.post(
            "/activities/Fake%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_duplicate_email_returns_error(self):
        """Arrange: email already registered; Act: POST signup with same email; Assert: 400 error"""
        activity_name = "Chess%20Club"
        email = "michael@mergington.edu"  # Already in participants
        
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()


class TestUnregisterFromActivity:
    """Test removing a participant from an activity"""

    def test_unregister_existing_participant(self):
        """Arrange: participant exists; Act: DELETE signup; Assert: participant removed"""
        # First, add a participant
        add_response = client.post(
            "/activities/Drama%20Club/signup?email=temporary@mergington.edu"
        )
        assert add_response.status_code == 200

        # Then remove them
        remove_response = client.delete(
            "/activities/Drama%20Club/signup?email=temporary@mergington.edu"
        )
        assert remove_response.status_code == 200
        data = remove_response.json()
        assert "Removed" in data["message"]

    def test_unregister_nonexistent_activity(self):
        """Arrange: invalid activity; Act: DELETE signup; Assert: 404 error"""
        response = client.delete(
            "/activities/Fake%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_participant_not_registered(self):
        """Arrange: email not in activity; Act: DELETE signup; Assert: 404 error"""
        response = client.delete(
            "/activities/Chess%20Club/signup?email=notregistered@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"].lower()
