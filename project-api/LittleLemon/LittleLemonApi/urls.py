from django.urls import path
from . import views

urlpatterns = [
    path('menu-items/', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('groups/', views.GroupView.as_view()),
    path('groups/<group_name>/users', views.GroupUserView.as_view()),
    path('groups/<group_name>/users/<int:id>', views.GroupUserView.as_view()),
    path('cart/menu-items', views.CartMenuItemView.as_view()),
]