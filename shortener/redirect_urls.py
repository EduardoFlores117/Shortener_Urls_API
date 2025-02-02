from django.urls import path
from .views import RedirectURLView

urlpatterns = [
    path('<str:short_code>/', RedirectURLView.as_view(), name='redirect_url'),
]
