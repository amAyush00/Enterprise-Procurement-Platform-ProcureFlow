import unittest
import json
from backend.app import create_app, db
from backend.config.settings import Config
from backend.models.user import User, Role
from backend.models.vendor import Vendor
from backend.models.product import Category, Product
from backend.models.purchase_request import PurchaseRequest
from backend.models.purchase_order import PurchaseOrder

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class EnterpriseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed roles
        roles = [
            Role(id=1, name='Admin'),
            Role(id=2, name='Procurement Officer'),
            Role(id=3, name='Manager'),
            Role(id=4, name='Employee')
        ]
        db.session.add_all(roles)

        # Seed test users with Password123
        pw_hash = '$2b$12$AG2BcKDp/o4e9Cift42LwuxHUQZuUPCsHB6RNI3/6CHk64E35dQIO'
        users = [
            User(id=1, role_id=1, username='admin', email='admin@enterprise.com', password_hash=pw_hash, first_name='Raghav', last_name='Sharma'),
            User(id=2, role_id=2, username='officer', email='officer@enterprise.com', password_hash=pw_hash, first_name='Rajesh', last_name='Verma'),
            User(id=3, role_id=3, username='manager', email='manager@enterprise.com', password_hash=pw_hash, first_name='Priyanka', last_name='Joshi'),
            User(id=4, role_id=4, username='employee', email='employee@enterprise.com', password_hash=pw_hash, first_name='Amit', last_name='Patil'),
            User(id=5, role_id=4, username='sneha', email='sneha@enterprise.com', password_hash=pw_hash, first_name='Sneha', last_name='Kulkarni'),
            User(id=6, role_id=4, username='vikram', email='vikram@enterprise.com', password_hash=pw_hash, first_name='Vikram', last_name='Malhotra'),
            User(id=7, role_id=4, username='ananya', email='ananya@enterprise.com', password_hash=pw_hash, first_name='Ananya', last_name='Roy'),
            User(id=8, role_id=4, username='rohit', email='rohit@enterprise.com', password_hash=pw_hash, first_name='Rohit', last_name='Sen')
        ]
        db.session.add_all(users)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_all_eight_users_authentication(self):
        """
        Verify that all 8 user accounts can successfully authenticate with Password123.
        """
        usernames = ['admin', 'officer', 'manager', 'employee', 'sneha', 'vikram', 'ananya', 'rohit']
        for u in usernames:
            response = self.client.post('/api/auth/login', json={
                'username': u,
                'password': 'Password123'
            })
            self.assertEqual(response.status_code, 200, f"Login failed for {u}")
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertIn('access_token', data['data'])
            self.assertEqual(data['data']['user']['username'], u)

    def test_invalid_password(self):
        """
        Verify that incorrect password fails authentication.
        """
        response = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.get_json()['success'])

if __name__ == '__main__':
    unittest.main()
