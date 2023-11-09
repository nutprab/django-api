from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group

from .permissions import CheckPermission, IsUserManager, IsUserDeliveryCrew, IsUserCustomer
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

    def get(self, request, group_name, id = -1):
        group_name = "DeliveryCrew" if group_name == "delivery-crew" else "Manager"
        users = User.objects.all().filter(groups__name=group_name)
        if id>0:
            users = users.filter(id=id)
        serializer_class = UserSerializer(users, many=True)
        return Response(serializer_class.data)
    
    def post(self, request, group_name):
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        group_name = "DeliveryCrew" if group_name == "delivery-crew" else "Manager"
        group = Group.objects.get(name=group_name)
        group.user_set.add(user)
        return_response = {
            "message" : "User with username {0} added to Group {1}".format(user.email, group.name)
        }
        return Response(return_response, status=status.HTTP_201_CREATED)
    
    def delete(self, request, group_name):
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        group_name = "DeliveryCrew" if group_name == "delivery-crew" else "Manager"
        group = Group.objects.get(name=group_name)
        group.user_set.remove(user)
        return_response = {
            "message" : "User with username {0} removed from Group {1}".format(user.email, group.name)
        }
        return Response(return_response, status=status.HTTP_200_OK)

class CartMenuItemView(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsUserCustomer]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=self.request.user)
        cart.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


class OrderView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser | IsUserManager | IsUserDeliveryCrew | IsUserCustomer]
    serializer_class = OrderSerializer
    
    def get_queryset(self, orderid=None):
        queryset = Order.objects.all()
        if IsUserCustomer:
            queryset = queryset.filter(user=self.request.user)
            if orderid is not None:
                queryset = queryset.filter(id=orderid)
        elif IsUserDeliveryCrew:
            queryset = queryset.filter(delivery_crew=self.request.user)
        return queryset
    
    def create(self, request, *args, **kwargs):
        if IsUserCustomer:
            usercart = Cart.objects.all().filter(user=request.user)
            if usercart.count() == 0:
                return_response = {
                    "message": "{0}'s Cart is Empty!".format(request.user.username)
                }
                return Response(return_response)
            data = request.data.copy()
            data["total"] = sum([item["price"] for item in usercart.values])
            data["user"] = request.user
            order_serializer = OrderSerializer(data=data)
            if order_serializer.is_valid():
                order_serializer.save()
                

