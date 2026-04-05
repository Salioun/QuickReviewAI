from django.urls import path
from . import views

urlpatterns = [
    path('reviews/', views.ReviewPostView.as_view()),
    path('reviews/<int:id>', views.ReviewGetView.as_view())
]
