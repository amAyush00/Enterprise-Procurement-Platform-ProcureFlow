import unittest
from backend.app import create_app, db
from backend.config.settings import Config

class TestConfig(Config):
    TESTING = True
    # Use SQLite in-memory database to run tests quickly without MySQL overhead
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_initialization(self):
        """
        Verify that the Flask app context initializes correctly.
        """
        self.assertFalse(self.app is None)

    def test_login_input_validation(self):
        """
        Verify that empty login requests return a 400 Bad Request error.
        """
        response = self.client.post('/api/auth/login', json={})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json['success'])

    def test_unauthorized_routes(self):
        """
        Verify that requesting protected endpoints without a token returns 401 Unauthorized.
        """
        response = self.client.get('/api/vendors')
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json['success'])

if __name__ == '__main__':
    unittest.main()
