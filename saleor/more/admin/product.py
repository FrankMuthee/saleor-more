# -*- coding: utf-8 -*-
from django.contrib import admin
from saleor.more.models import Product, ProductFeatureValue
from saleor.product.models import ProductImage, Category
from saleor.more.forms import ProductForm
from django.utils.translation import ugettext_lazy as _


class ProductImagesInline(admin.TabularInline):
    """ Inline for Product's images """
    model = ProductImage
    extra = 1
    max_num = 1
    verbose_name = "Imágenes de producto"

    def queryset(self, request):
        qs = super(ProductImagesInline, self).queryset(request).prefetch_related(
            'thumbnail_set')  # .select_related('attributes__attributevalue')
        return qs


class ProductFeatureInline(admin.TabularInline):
    """ Inline for Product's features """
    model = ProductFeatureValue
    fields = ('feature', 'value')



class ProductAdmin(admin.ModelAdmin):
    """ Product  admin. It has an inline for productvariants """
    list_display = ('name','category', 'featured')
    form = ProductForm
    fieldsets = (
        (None, {
            'fields': ('name', 'sku', 'description','price', 'featured', 'order', 'weight'),
        }),
        (_("Category") +'', {'fields': ('categories',)}),

    )
    inlines = [ProductImagesInline, ProductFeatureInline]

    tabs = (("General", (None, _("Category")+'')), (
        _("Images")+'', (ProductImagesInline,)), (_("Features")+'', (ProductFeatureInline,)))
    
    def category(self, obj):
        return obj.get_first_category()
    category.short_description = Category._meta.verbose_name
    category.admin_order_field = 'categories__name'
