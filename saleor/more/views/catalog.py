from django.views.generic import TemplateView, ListView
from django.http import HttpResponse
from saleor.product.models import Category, Product
from saleor.more.models import Product
from saleor.more.models.product import ProductManager
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.conf import settings

class CatalogView(ListView):
    template_name = 'more/catalog/catalog.html'
    queryset = Product.objects.none()
    context_object_name = 'products_list'
    paginate_by = settings.PRODUCTS_PER_PAGE

    def get_queryset(self):
        self.category = None
        if 'cat_id' in self.kwargs:
            self.category = get_object_or_404(Category, pk=self.kwargs['cat_id'])
        if self.category is None:
            return Product.objects.all() # TODO que productoss obtener por defecto?
        # Queryset overriding
        return Product.objects.get_products_from_cat(self.category)

    
    def get_context_data(self, **kwargs):
        """ Show all products if no category, else, filter by cat """
        context = super(CatalogView, self).get_context_data( **kwargs)
        category_list = Category.objects.all()
        context['category'] = self.category
        context['category_list'] = category_list
        return context
