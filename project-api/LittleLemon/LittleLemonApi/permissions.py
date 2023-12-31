from rest_framework import permissions

#align permission class to not use hardcoded strings
#refactor to make it more meaningful

class IsUserManager(permissions.BasePermission):
    def has_permission(self, request, view=None):
        if request.user and request.user.groups.filter(name="Manager"):
            return True
        return False

class IsUserDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view=None):
        if request.user and request.user.groups.filter(name="DeliveryCrew"):
            return True
        return False

class IsUserCustomer(permissions.BasePermission):
    def has_permission(self, request, view=None):
        if request.user:
            if not (request.user.groups.filter(name="DeliveryCrew") or request.user.groups.filter(name="Manager")) :
                return True
        return False