from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.forms.models import model_to_dict

import datetime

from .permissions import IsUserManager, IsUserDeliveryCrew, IsUserCustomer
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
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsAdminUser | IsUserManager]
        else:
            self.permission_classes = []
        return super(MenuItemView, self).get_permissions()

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsAdminUser | IsUserManager]
        else:
            self.permission_classes = []
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

    def post(self, request):
        id = int(request.data.get("menuitem_id"))
        menuitem = MenuItem.objects.all().filter(id=id)
        menuitemserializer = MenuItemSerializer(menuitem, many=True)
        unitprice = menuitemserializer.data[0]["price"]
        quantity = request.data.get("quantity")
        totalprice = str(round(float(unitprice) * float(quantity),2))
        existingCart = Cart.objects.all().filter(user=request.user, menuitem=id)
        count = existingCart.count()
        data = {
            "user": request.user.id,
            "menuitem": id,
            "quantity": quantity,
            "unit_price": unitprice,
            "price": totalprice
        }
        if count>0:
            existingCartSerializer = CartSerializer(instance=existingCart[0], data=data)
            existingCartSerializer.is_valid()
            existingCartSerializer.validated_data
            existingCartSerializer.save()
            return Response({"existingCart": existingCartSerializer.data}, status = status.HTTP_200_OK)
        else:
            newCartSerializer = CartSerializer(data=data)
            newCartSerializer.is_valid()
            # newCartSerializer.errors
            newCartSerializer.validated_data
            newCartSerializer.save()
            return Response({"newCart": newCartSerializer.data}, status = status.HTTP_201_CREATED)

    def delete(self, request):
        cart = Cart.objects.filter(user=request.user, menuitem_id=request.data.get("menuitem_id"))
        cart.delete()
        return Response({"deletedItem": request.data.get("menuitem_id")},status = status.HTTP_204_NO_CONTENT)

class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsUserCustomer]
        elif self.request.method == "GET":
            self.permission_classes = [IsAdminUser | IsUserManager | IsUserDeliveryCrew | IsUserCustomer]
        return super().get_permissions()

    
    def get_queryset(self):
        queryset = Order.objects.all()
        if self.request.user.is_staff or self.request.user.groups.filter(name="Manager"):
            queryset = queryset
        elif self.request.user.groups.filter(name="DeliveryCrew"):
            queryset = queryset.filter(delivery_crew=self.request.user)
        elif not (self.request.user.groups.filter(name="DeliveryCrew") or self.request.user.groups.filter(name="Manager")):
            queryset = queryset.filter(user=self.request.user)
        return queryset
    
    def get_user_cart(self, user):
        return Cart.objects.all().filter(user=user)

    def get_user_open_order(self, user):
        return Order.objects.all().filter(user=user, status=0)

    def save_serializer(self, serializer, data, instance = None):
        success = 0
        tempserializer = None
        if instance==None:
            tempserializer = serializer(data=data)
        else:
            tempserializer = serializer(instance=instance, data=data)
        
        if tempserializer:
            tempserializer.is_valid()
            tempserializer.validated_data
            tempserializer.save()
            success=1
        return success

    def create_new_order(self, request, userCart):
        total_price = sum([item["price"] for item in userCart.values()])
        orderData = {
            "user" : request.user.id,
            "deliver_crew": None,
            "status": 0,
            "total": total_price,
            "date": datetime.date.today()
        }
        newOrderSerializer = OrderSerializer(data=orderData)
        newOrderSerializer.is_valid()
        newOrderSerializer.validated_data
        newOrderSerializer.save()

        newOrderId = newOrderSerializer.data["id"]

        for item in userCart.values():
            orderItemData = {
                "order_id": newOrderId,
                "menuitem_id": item["id"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "price": item["price"]    
            }
            orderItemSerializer = OrderItemSerializer(data=orderItemData)
            orderItemSerializer.is_valid()
            orderItemSerializer.validated_data
            orderItemSerializer.save()

        response_data = {
            "OrderData": newOrderSerializer.data,
            "OrderItemData": orderItemSerializer.data,
            "CartData": userCart.values()
        }
        return "New Order Created", response_data

    def update_existing_open_order(self, request, userOrder, userCart):
        userOrderId = userOrder.values()[0]["id"]
        total_price = sum([item["price"] for item in userCart.values()])
        for item in userCart.values():
            orderItemData = {
                "order_id": userOrderId,
                "menuitem_id": item["id"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "price": item["price"]    
            }
            existingOrderItem = OrderItem.objects.all().filter(order=userOrderId, menuitem_id=item["id"])
            orderItemSerializer = None
            if existingOrderItem.count() > 0:
                orderItemData["quantity"] += existingOrderItem.values[0]["quantity"]
                orderItemData["price"] = orderItemData["unit_price"] * orderItemData["quantity"]
                total_price += orderItemData["price"]
                orderItemSerializer = OrderItemSerializer(instance=existingOrderItem[0], data=orderItemData)
            else:
                orderItemSerializer = OrderItemSerializer(data=orderItemData)
            orderItemSerializer.is_valid()
            orderItemSerializer.validated_data
            orderItemSerializer.save()

        orderData = {
            "user" : request.user.id,
            "deliver_crew": None,
            "status": 0,
            "total": total_price,
            "date": datetime.date.today()
        }
        newOrderSerializer = OrderSerializer(instance=userOrder[0], data=orderData)
        newOrderSerializer.is_valid()
        newOrderSerializer.validated_data
        newOrderSerializer.save()
        
        response_data = {
            "OrderData": newOrderSerializer.data,
            "OrderItemData": orderItemSerializer.data,
            "CartData": userCart.values
        }
        return "Updated existing order", response_data

    def post(self, request):
        response = {
            "message": "",
            "data": {}
        }
        response_status = status.HTTP_200_OK

        userCart = self.get_user_cart(request.user)
        userOrder = self.get_user_open_order(request.user)
        userHasCartItem = userCart.count()
        userHasExistingOpenOrder = userOrder.count()
        if userHasCartItem:
            if userHasExistingOpenOrder:
                response["message"], response["data"] = self.update_existing_open_order(request, userOrder=userOrder, userCart=userCart)
                response_status = status.HTTP_201_CREATED
            else:
                response["message"], response["data"] = self.create_new_order(request, userCart=userCart)
                response_status = status.HTTP_201_CREATED
            userCart.delete()
        else:
            response["message"] = "{0}'s Cart is Empty!".format(request.user.username)
            response_status = status.HTTP_404_NOT_FOUND
        return Response(response, response_status)

class OrderItemsView(generics.GenericAPIView):
    serializer_class = OrderItemSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsUserCustomer]
        elif self.request.method == "PUT":
            self.permission_classes = [IsAdminUser | IsUserManager]
        elif self.request.method == "PATCH":
            self.permission_classes = [IsAdminUser | IsUserManager | IsUserDeliveryCrew]
        elif self.request.method == "DELETE":
            self.permission_classes == [IsAdminUser | IsUserManager]
        return super().get_permissions()
    
    def get(self, request, id):
        order = Order.objects.all().filter(user=request.user, id=id)
        response = {
            "Order": "Either Order doesnot exist or Order does Not belog to you",
            "OrderItems": "No Order Items to Show"
        }
        reposnse_status = status.HTTP_404_NOT_FOUND
        if order.count() > 0 :
            response["Order"] = OrderSerializer(order, many=True).data
            orderItems = OrderItem.objects.all().filter(order_id=id)
            orderItemsSerializer = OrderItemSerializer(orderItems, many=True)
            response["OrderItems"] = orderItemsSerializer.data
            reposnse_status = status.HTTP_200_OK
        return Response(response, status=reposnse_status)

    def put(self, request, id):
        deliveryCrew_id = request.data.get("delivery_crew")
        order = Order.objects.filter(id=id)
        response = {}
        response_status = status.HTTP_404_NOT_FOUND
        user = User.objects.filter(id=deliveryCrew_id, groups__name="DeliveryCrew")
        if user.count() == 0:
            response["Error"] = "Delivery Crew member does not Exit"
        else:
            if order.count()>0:
                deliveryCrew = {
                    "delivery_crew": deliveryCrew_id
                }
                orderSerializer = OrderSerializer(instance=order[0], data=deliveryCrew, partial=True)
                orderSerializer.is_valid()
                orderSerializer.validated_data
                orderSerializer.save()
                response["Order"] = orderSerializer.data
                response_status = status.HTTP_200_OK
            else: 
                response["Order"] = "Order doesnot exist"
        return Response(response, status = response_status)
    
    def patch(self, request, id):
        response = {}
        response_status = status.HTTP_404_NOT_FOUND
        order = Order.objects.filter(id=id)
        if request.user.groups.filter(name="DeliveryCrew"):
            order = order.filter(delivery_crew=request.user)
            if order.count()==0:
                response["Error"] = "This Order does not belong to you"
                return Response(response, status = response_status)
            
        delivery_status = request.data.get("status")
        if order.count()>0:
            deliveryStatus = {
                "status": delivery_status
            }
            orderSerializer = OrderSerializer(instance=order[0], data=deliveryStatus, partial=True)
            orderSerializer.is_valid()
            orderSerializer.validated_data
            orderSerializer.save()
            response["Order"] = orderSerializer.data
            response_status = status.HTTP_200_OK
        else: 
            response["Order"] = "Order doesnot exist"
        return Response(response, status = response_status)
    
    def delete(self, request, id):
        response = {"status":"Item Deleted"}
        response_status = status.HTTP_204_NO_CONTENT
        order = Order.objects.filter(id=id)
        order.delete()
        return Response(response, status = response_status)