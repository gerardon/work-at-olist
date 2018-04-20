from django.urls import path


from .views import CallRecordsListCreate

urlpatterns = [
    path('records/', CallRecordsListCreate.as_view(), name='records'),
]
