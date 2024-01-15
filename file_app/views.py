from file_app.tasks import upload_file_to_s3_task
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from utils.s3 import  delete_file_from_s3, rename_file_in_s3, get_file
from  .models import UploadedFile
from file_manager.config import MAX_FILE_SIZE_BYTES
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate
from .serializers import UserSerializer,UploadedFileSerializer
from rest_framework.decorators import authentication_classes
from rest_framework.authtoken.models import Token 
from rest_framework.authentication import TokenAuthentication

from django.core.validators import FileExtensionValidator
from botocore.exceptions import ClientError
from django.http import HttpResponse
from django.core.exceptions import ValidationError



# Upload a file 
@api_view(['POST'])
@authentication_classes([TokenAuthentication])  # Add TokenAuthentication
@permission_classes([IsAuthenticated])  # Require authenticated user
def upload_file(request):
    """
    Uploads a file to S3.

    Args:
        request: Django HTTP request containing the file.

    Returns:
        Response with a success or error message.
    """
    if request.method == 'POST':
        # Access the authenticated user using request.user
        authenticated_user = request.user
        try:
            file = request.FILES['file']
        
            allowed_extensions = ['jpg', 'jpeg', 'png', 'pdf']  # Add your allowed extensions
            validate_extension = FileExtensionValidator(allowed_extensions)
            validate_extension(file)

            # Validate file size

            if file.size > MAX_FILE_SIZE_BYTES:
                return Response({'message': f'File size exceeds the maximum limit of 10 MB.'}, status=400)

            # Generate a unique key for your S3 object, e.g., using the file name
            # unique_filename = f"{uuid.uuid4()}-{file.name}"
            s3_key = f"uploads/{authenticated_user.username}/{file.name}"


            upload_file_to_s3_task.delay(file, s3_key)
            uploaded_file = UploadedFile(file=file, file_name=file.name, file_size=file.size,user = authenticated_user)
            uploaded_file.save()

            return Response({'message': 'File uploaded successfully'})

        except Exception as e:
            return Response({'message': f'Error uploading file: {str(e)}'}, status=500)

    return Response({'message': 'Invalid request method'}, status=400)

# Delete A file
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication]) 
def delete_file(request):
    """
    Deletes a file from S3.
    Args:
        request: Django HTTP request containing the file key to delete.
    Returns:
        Response with a success or error message.
    """
    if request.method == 'POST':
        authenticated_user = request.user
        try:
            document_id = request.data.get('file_id')
            uploaded_file = UploadedFile.objects.get(uuid=document_id,user=authenticated_user)
            old_s3_key = f"uploads/{uploaded_file.user.username}/{uploaded_file.file_name}"

            delete_file_from_s3(old_s3_key)
            uploaded_file.delete()

            return Response({'message': 'File deleted successfully'})

        except Exception as e:
            return Response({'message': "UUid Not Exits!"}, status=404)

    return Response({'message': 'Invalid request method'}, status=400)

# Rename file 
@api_view(['POST'])
@authentication_classes([TokenAuthentication])  # Add TokenAuthentication
@permission_classes([IsAuthenticated])  # Require authenticated user
def rename_file(request):
    """
    Renames a file in S3.
    Args:
        request: Django HTTP request containing the old and new file keys.
    Returns:
        Response with a success or error message.
    """
    if request.method == 'POST':
        authenticated_user = request.user

        try:
            file_id = request.data.get('file_id')
            new_filename = request.data.get('new_filename')
            uploaded_file = UploadedFile.objects.get(uuid=file_id,user=authenticated_user)
                

            # # Generate the new S3 key with the new filename
            new_s3_key = f"uploads/{uploaded_file.user.username}/{new_filename}"
            old_s3_key = f"uploads/{uploaded_file.user.username}/{uploaded_file.file_name}"
      
            rename_file_in_s3(old_s3_key, new_s3_key) 

        
            # Update the database with the new filename and S3 key
            uploaded_file.file_name = new_filename
            uploaded_file.save()

            return Response({'message': 'File renamed successfully'},status=200)

        except Exception as e:
            print(e)
            return Response({'message': "File Id Not Exits!"}, status=404)

    return Response({'message': 'Invalid request method'}, status=400)


#User registeration
@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#User login
@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    token = Token.objects.get_or_create(user=user)
    if user:
        serializer = UserSerializer(user)
        tokan = str(token)
        return Response({"Data":serializer.data, "Token":tokan}, status=status.HTTP_200_OK)
    return Response({'message': 'Invalid username or password',}, status=status.HTTP_401_UNAUTHORIZED)



#List all file of a User
@api_view(['GET'])
@authentication_classes([TokenAuthentication]) 
@permission_classes([IsAuthenticated])
def uploaded_file_list(request):
    """
    List all uploaded files.
    """
    files = UploadedFile.objects.filter(user=request.user)
    serializer = UploadedFileSerializer(files, many=True)
    return Response(serializer.data)

# download File
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def download_file(request):    
    authenticated_user = request.user
    document_id = request.data.get('file_id')

    try:
        uploaded_file = UploadedFile.objects.get(uuid=document_id, user=authenticated_user)


        s3_key = f"uploads/{authenticated_user.username}/{uploaded_file.file_name}"
        print(s3_key)
        # Fetch the file content from S3
        response = get_file(s3_key)
        return response

    except UploadedFile.DoesNotExist:
        return HttpResponse("Key not found!", status=404)

    except ClientError as e:
        return HttpResponse(f"Error fetching file from S3: {e}", status=500)
    except ValidationError:
        return HttpResponse("File does not exist", status=404)