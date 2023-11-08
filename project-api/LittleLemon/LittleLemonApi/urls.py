from django.urls import path
from . import views

urlpatterns = [
    path('menu-items/', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('groups/', views.GroupView.as_view()),
    path('groups/<group_name>/users/', views.GroupUserView.as_view()),
]