from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.http import HttpResponse
from saleor.more.models import Product
from saleor.more.models.product import VirtualProductVariant
from saleor.product.models import ProductVariant
from saleor.product.models import Category
from saleor.cart.forms import AddToCartForm
from saleor.cart import Cart
from django import forms
import json
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _


class ProductAddForm(AddToCartForm):

    """ Form in product_detail view used to add products to cart """
    variant = forms.ModelChoiceField(
        queryset=ProductVariant.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        product = kwargs['product']

        super(ProductAddForm, self).__init__(*args, **kwargs)
        self.fields['variant'].queryset = product.variants.all()

    def get_variant(self, cleaned_data):
        print "getting cleaned data"
        variant = cleaned_data['variant']
        if variant is None:
            variant = self.product.get_virtual_variant()
            print "adding virtual variant", variant
        return variant


class ProductDetail(DetailView):

    """Product detail view"""

    template_ = "more/product_detail.html"
    model = Product
    context_object_name = 'product'
    obj = None
    form = None

    def get_object(self, queryset=None):
        """ Returns product instance. The instance is cached to reduce queries """
        if self.obj is None:
            self.obj = super(ProductDetail, self).get_object(queryset)
        return self.obj

    def get_form(self, data=None, cart=None):
        if self.form is None:
            self.form = ProductAddForm(
                product=self.get_object(), cart=cart, data=data)
        return self.form

    def post(self, request, *args, **kwargs):
        """ POST Request. Process Addtocart form """
        cart = Cart.for_session_cart(request.cart, discounts=request.discounts)
        error = False
        try:
            form = self.get_form(data=request.POST, cart=cart)
            if form.is_valid():
                print("form valid")
                # Form valid
                form.save()
                msg = _('Successfully added product to cart.')
                messages.success(request, msg)

            else:
                error = True
                print "ERRORS ", form.errors
        except Exception as e:
            error = True
            print("error adding to cart", e)
        if error:
            msg = _('Error. Could not add product to cart.')
            messages.error(request, msg)

        if request.is_ajax():
            # Is ajax
            if error:
                return HttpResponse("ERROR")
            return HttpResponse("SUCCESS")
        return super(ProductDetail, self).get(request, *args, **kwargs)

    def get_queryset(self):
        p = super(ProductDetail, self).get_queryset().prefetch_related(
            'images', 'variants')
        return p

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        product = self.get_object()
        context['category'] = product.get_first_category()
        context['category_list'] = Category.objects.all()
        context['form'] = self.get_form()
        product.get_price_with_discount(self.request.discounts)
        return context
