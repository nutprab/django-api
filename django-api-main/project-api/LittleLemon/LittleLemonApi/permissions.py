from rest_framework import permissions

#align permission class to not use hardcoded strings
#refactor to make it more meaningful

class CheckPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user:
            if request.user.groups.filter(name="Manager"):
                return "Manager"
            elif request.user.groups.filter(name="Delivery Crew"):
                return "Delivery Crew"
        return "No Perm"

class IsUserManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name="Manager"):
            return True
        return False

class IsUserDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name="Delivery Crew"):
            return True
        return False