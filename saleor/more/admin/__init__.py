from django.contrib import admin
from catalog import CategoryAdmin
from product import ProductAdmin
from discount import CatalogDiscountAdmin

from saleor.more.models import Product, CatalogDiscount

from saleor.product.models import Category, Discount

try:
    admin.site.unregister(Category)
    admin.site.unregister(Discount)
except:
    pass
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(CatalogDiscount, CatalogDiscountAdmin)
