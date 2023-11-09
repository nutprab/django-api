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
    user = UserSerializer
    menuitem = MenuItemSerializer
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer
    delivery_crew = UserSerializer
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']

class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer
    menuitem = MenuItemSerializer
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']
