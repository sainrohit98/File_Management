from django.test import TestCase
from rest_framework.test import APIClient ,APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import UploadedFile
from .serializers import UploadedFileSerializer
from .views import delete_file

class UploadedFileListViewTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)

        # Create a test client
        self.client = APIClient()

        # Authenticate the client with the created user's token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

        # Create some test uploaded files for the user
        self.file1 = UploadedFile.objects.create(user=self.user, file_name='file1.txt', file_size=1024)
        self.file2 = UploadedFile.objects.create(user=self.user, file_name='file2.txt', file_size=2048)

    def test_uploaded_file_list_view(self):
        # Make a GET request to the uploaded_file_list view
        response = self.client.get('/uploaded_file_list')

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response data contains the serialized files for the user
        expected_data = UploadedFileSerializer([self.file1, self.file2], many=True).data
        self.assertEqual(response.data, expected_data)

    def tearDown(self):
        # Clean up the test files and user
        UploadedFile.objects.filter(user=self.user).delete()
        self.user.delete()



class DeleteFileViewTest(TestCase):

    def setUp(self):
        # Create a test user and token
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)

        # Create a test uploaded file
        self.uploaded_file = UploadedFile.objects.create(
            user=self.user,
            file_name='test_file.txt',
            file_size=1024,
        )

        # Create an API client and set the Authorization header with the token
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_delete_file_successfully(self):
        # Send a POST request to delete the file
        response = self.client.post('/deletefile', {'file_id': str(self.uploaded_file.uuid)})

        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the file is deleted
        self.assertFalse(UploadedFile.objects.filter(pk=self.uploaded_file.pk).exists())

    def test_delete_file_invalid_uuid(self):
        # Send a POST request with an invalid UUID
        response = self.client.post('/deletefile', {'file_id': 'invalid-uuid'})

        # Check that the response status is 404 Internal Server Error
        self.assertEqual(response.status_code, 404)

        # Check the response message
        self.assertEqual(response.data['message'], "UUid Not Exits!")

    def test_delete_file_not_authenticated(self):
        # Use an API client without authentication
        unauthenticated_client = APIClient()

        # Send a POST request to delete the file without authentication
        response = unauthenticated_client.post('/deletefile', {'file_id': str(self.uploaded_file.uuid)})

        # Check that the response status is 401 Unauthorized
        self.assertEqual(response.status_code, 401)

        # Check the response message
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
    
class RenameFileViewTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)

        # Create a test client
        self.client = APIClient()

        # Authenticate the client with the created user's token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

        # Create a test uploaded file for the user
        self.file = UploadedFile.objects.create(user=self.user, file_name='Profile.pdf', file_size=1024)

    def test_rename_file_view(self):
        # Make a POST request to the rename_file view
        data = {
            'file_id': str(self.file.uuid),  # Convert UUID to string
            'new_filename': 'new_file.txt'
        }
        print(data)
        response = self.client.post('/renamefile', data)
        print(response.content)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the file in the database has been renamed
        self.file.refresh_from_db()
        self.assertEqual(self.file.file_name, 'new_file.txt')


    def tearDown(self):
        # Clean up the test files and user
        # UploadedFile.objects.all().delete()
        # self.user.delete()
        pass

class DownloadFileViewTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)

        # Create a test client
        self.client = APIClient()

        # Authenticate the client with the created user's token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

        # Create a test uploaded file for the user
        self.file = UploadedFile.objects.create(user=self.user, file_name='new_file.txt', file_size=1024)

    def test_download_file_view(self):
        # Make a GET request to the download_file view
        response = self.client.post('/download',{"file_id" : str(self.file.uuid)})
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response has the correct content type
        self.assertEqual(response['Content-Type'], 'application/octet-stream')

        # Check if the response has the correct content disposition
        expected_filename = 'new_file.txt'
        self.assertEqual(
            response['Content-Disposition'], f'attachment; filename="{expected_filename}"'
        )

    def test_download_file_nonexistent_file(self):
        # Make a GET request to the download_file view with a nonexistent file ID
        response = self.client.post('/download',{"file_id" : 'nonexistent_uuid'})

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Check if the response content indicates that the key is not found
        self.assertEqual(response.content, b'File does not exist')