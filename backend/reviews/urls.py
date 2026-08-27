from django.urls import path
from . import views

urlpatterns = [
    path('reviews/', views.ReviewListView.as_view()),
    path('reviews/create', views.ReviewPostView.as_view()),
    path('reviews/<int:id>/', views.ReviewGetView.as_view())
]
