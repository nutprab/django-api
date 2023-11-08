from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group

from .permissions import CheckPermission, IsUserManager, IsUserDeliveryCrew
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    UserSerializer,
    GroupSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer
)


# Create your views here.
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    ordering_fields = ["title","price"]
    search_fields = ["title", "category__title"]
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ["POST"]:
            self.permission_classes = [IsAdminUser | IsUserManager]
        return super(MenuItemView, self).get_permissions()

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsAdminUser | IsUserManager]
        return super(SingleMenuItemView, self).get_permissions()

class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ["POST"]:
            self.permission_classes = [IsAdminUser | IsUserManager]
        return super(CategoryView, self).get_permissions()

class GroupView(generics.ListAPIView):
    permission_classes = [IsAdminUser | IsUserManager]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class GroupUserView(generics.GenericAPIView):
    permission_classes = [IsAdminUser | IsUserManager]

    def get(self, request, group_name):
        group_name = "Delivery Crew" if group_name == "delivery-crew" else "Manager"
        users = User.objects.all().filter(groups__name=group_name)
        serializer_class = UserSerializer(users, many=True)
        return Response(serializer_class.data)
    
    def post(self, request, group_name):
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        group_name = "Delivery Crew" if group_name == "delivery-crew" else "Manager"
        group = Group.objects.get(name=group_name)
        group.user_set.add(user)
        return_response = {
            "message" : "User with username {username} added to Group {group_name}"
        }
        return Response(return_response, status=status.HTTP_201_CREATED)
    
    def delete(self, request, group_name):
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        group_name = "Delivery Crew" if group_name == "delivery-crew" else "Manager"
        group = Group.objects.get(name=group_name)
        group.user_set.remove(user)
        return_response = {
            "message" : "User with username {username} removed from Group {group_name}"
        }
        return Response(return_response, status=status.HTTP_200_OK)

