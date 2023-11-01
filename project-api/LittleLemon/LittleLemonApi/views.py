from django.shortcuts import render
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer

from rest_framework import generics

# Create your views here.
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer