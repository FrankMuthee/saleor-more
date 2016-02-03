from saleor.order.models import Order
from saleor.order import admin as order_admin

class OrderAdmin(order_admin.OrderAdmin):
    actions = None
    def has_delete_permission(self,request, object=None):
        return False
