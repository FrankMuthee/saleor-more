from django.contrib import admin
from catalog import CategoryAdmin
from product import ProductAdmin
from discount import CatalogDiscountAdmin
from order import OrderAdmin

from saleor.more.models import Product, CatalogDiscount
from saleor.order.models import Order 
from saleor.product.models import Category, Discount

try:
    #Unregister default saleor admins
    admin.site.unregister(Category)
    admin.site.unregister(Discount)
    admin.site.unregister(Order)
except:
    pass

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(CatalogDiscount, CatalogDiscountAdmin)
admin.site.register(Order, OrderAdmin)
