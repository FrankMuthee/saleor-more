from django.contrib import admin
from saleor.product.models import Category
from mptt.admin import MPTTModelAdmin
from saleor.more.models import CategoryImage

class CategoryImageInline(admin.TabularInline):
    model = CategoryImage
    extra = 1
    max_entries = 1
    max_num = 1
    can_delete = False


class CategoryAdmin(MPTTModelAdmin):
    list_display = ('tabbed_name', )
    inlines = [CategoryImageInline]

    def tabbed_name(self, obj):
        return 2 * '<i class="fa fa-minus "></i>' * obj.level + ' ' + obj.name
    tabbed_name.allow_tags = True
    tabbed_name.short_description = Category._meta.verbose_name
