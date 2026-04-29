"""
Comprehensive tests for High School Management System API

All tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and fixtures
- Act: Execute the action being tested
- Assert: Verify the results
"""

import pytest


class TestRootEndpoint:
    """Tests for the root GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Verify that GET / redirects to /static/index.html"""
        # Arrange
        expected_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_url

    def test_root_allows_redirect_following(self, client):
        """Verify that GET / can be followed to access the static file"""
        # Arrange
        # Act
        response = client.get("/", follow_redirects=True)

        # Assert
        assert response.status_code == 200


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""

    def test_get_all_activities_returns_nine_activities(self, client):
        """Verify that GET /activities returns all 9 activities"""
        # Arrange
        expected_activity_count = 9
        expected_activities = {
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Soccer Club", "Art Club", "Drama Club", "Debate Club", "Science Club"
        }

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        assert set(activities.keys()) == expected_activities

    def test_activity_structure_contains_required_fields(self, client):
        """Verify that each activity has required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert required_fields == set(activity_data.keys()), \
                f"Activity '{activity_name}' missing required fields"

    def test_activity_data_types_are_correct(self, client):
        """Verify that activity fields have correct data types"""
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            assert all(isinstance(email, str) for email in activity_data["participants"])

    def test_chess_club_has_initial_participants(self, client):
        """Verify chess club has the expected initial participants"""
        # Arrange
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]

        # Assert
        assert chess_club["participants"] == expected_participants


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_success(self, client):
        """Verify that a new student can successfully sign up for an activity"""
        # Arrange
        activity_name = "Chess Club"
        new_student_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student_email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {new_student_email} for {activity_name}"

    def test_signup_adds_student_to_participants_list(self, client):
        """Verify that after signup, the student appears in the participants list"""
        # Arrange
        activity_name = "Programming Class"
        new_student_email = "anotherstu@mergington.edu"

        # Act
        # First, sign up the student
        client.post(f"/activities/{activity_name}/signup", params={"email": new_student_email})

        # Then, retrieve the activities to verify the student was added
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert new_student_email in activities[activity_name]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Verify that signup for a non-existent activity returns 404"""
        # Arrange
        nonexistent_activity = "Underwater Basket Weaving"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student_returns_400(self, client):
        """Verify that signup fails when student is already enrolled"""
        # Arrange
        activity_name = "Chess Club"
        existing_student_email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_student_email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_same_student_multiple_activities(self, client):
        """Verify that a student can sign up for multiple different activities"""
        # Arrange
        student_email = "versatile@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Club"]

        # Act
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student_email}
            )
            # Assert each signup is successful
            assert response.status_code == 200

        # Assert: Verify student is in all activities
        response = client.get("/activities")
        activities = response.json()
        for activity_name in activities_to_join:
            assert student_email in activities[activity_name]["participants"]

    def test_signup_duplicate_attempt_fails_second_time(self, client):
        """Verify that second signup attempt for same activity returns 400"""
        # Arrange
        activity_name = "Debate Club"
        student_email = "debater@mergington.edu"

        # Act
        # First signup should succeed
        response_first = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Second signup with same email should fail
        response_second = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )

        # Assert
        assert response_first.status_code == 200
        assert response_second.status_code == 400
        assert response_second.json()["detail"] == "Student already signed up for this activity"


class TestStaticFilesIntegration:
    """Tests for static file serving integration"""

    def test_static_index_html_accessible(self, client):
        """Verify that /static/index.html is accessible"""
        # Arrange
        # Act
        response = client.get("/static/index.html")

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_static_app_js_accessible(self, client):
        """Verify that /static/app.js is accessible"""
        # Arrange
        # Act
        response = client.get("/static/app.js")

        # Assert
        assert response.status_code == 200
        assert "javascript" in response.headers.get("content-type", "").lower()

    def test_static_styles_css_accessible(self, client):
        """Verify that /static/styles.css is accessible"""
        # Arrange
        # Act
        response = client.get("/static/styles.css")

        # Assert
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
