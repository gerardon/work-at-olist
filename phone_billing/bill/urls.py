from django.urls import path


from .views import BillSearchView

urlpatterns = [
    path('<str:subscriber>/', BillSearchView.as_view(), name='search'),
]
