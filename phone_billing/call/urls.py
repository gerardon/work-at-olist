from django.urls import path


from .views import CallRecordsListCreate, CallRecordRetrieveUpdate

urlpatterns = [
    path('records/', CallRecordsListCreate.as_view(), name='records'),
    path('record/<int:pk>/', CallRecordRetrieveUpdate.as_view(),
         name='record_detail'),
]
