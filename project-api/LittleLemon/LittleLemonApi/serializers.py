from rest_framework import serializers
from django.contrib.auth.models import Group, User
from .models import Category, MenuItem, Cart, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]

class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    class Meta:
        model = Cart
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    delivery_crew = UserSerializer(read_only=True)
    class Meta:
        model = Order
        fields = "__all__"

class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']
