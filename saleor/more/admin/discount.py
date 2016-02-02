from django.contrib import admin
from saleor.more.models import CatalogDiscountRule, CatalogDiscount

class CatalogDiscountRuleInline(admin.StackedInline):
    model = CatalogDiscountRule
    extra = 1
    fields = ['use_or', 'rtype', 'category', 'product']

class CatalogDiscountAdmin(admin.ModelAdmin):
    model = CatalogDiscount
    inlines = [CatalogDiscountRuleInline]
    change_form_template = 'web_shop/admin/change_form.html'
    list_display = ('id', 'name', 'description','activated_by_coupon' ,'coupon', 'date_from', 'date_to', 'enabled')
    list_display_links = ('id', 'name')
