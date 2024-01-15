from django.urls import path
from . import views

urlpatterns = [
    path('uploadfile', views.upload_file, name='upload_file'),
    path('deletefile', views.delete_file, name='delete_file'),
    path('renamefile', views.rename_file, name='rename_file'),
    # path('listfiles', views.list_files, name='list_files'),
    path('register', views.register_user, name='register_user'),
    path('login', views.login_user, name='login_user'),
    path('uploaded_file_list', views.uploaded_file_list, name='uploaded_file_list'),
    path('download', views.download_file, name='download_file'),
    


]
