from django.test import TestCase, Client
from django.contrib.auth.models import User
from uploads.models import File

class SecurityTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        self.user_a = User.objects.create_user('user_a', 'a@test.com', 'pass')
        self.user_b = User.objects.create_user('user_b', 'b@test.com', 'pass')
        
        # Create a file belonging to User A
        self.file_a = File.objects.create(user=self.user_a, original_filename="secret.txt")

    def test_unauthorized_deletion_fails(self):
        # 1. Log in as User B
        self.client.login(username='user_b', password='pass')
        
        # 2. Try to delete User A's file
        response = self.client.post(f'/dashboard/delete_file/{self.file_a.id}/')
        
        # 3. Assert it failed (404 as per your view logic)
        self.assertEqual(response.status_code, 404)
        
        # 4. Assert the file STILL exists in the DB
        self.assertTrue(File.objects.filter(id=self.file_a.id).exists())