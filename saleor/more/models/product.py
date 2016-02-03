# -*- coding: utf-8 -*-
#from saleor.product.models import Product, PhysicalProduct, StockedProduct
from saleor.product import models as saleor_models
from django_prices.models import PriceField
from django.conf import settings
from django.db import models
from common import BaseModel
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from collections import OrderedDict
import operator
from django.utils.text import slugify
from django.utils.encoding import python_2_unicode_compatible, smart_text
from satchless.item import Item
from django.core.urlresolvers import reverse


class Feature(BaseModel):
    name = models.CharField(_("Name"), max_length=200)

    def __unicode__(self):
        return self.name

    class Meta(BaseModel.Meta):
        verbose_name = _('Feature')  # 'Caracteristica'
        verbose_name_plural = _('Features')  # 'Caracteristicas'
        ordering = ['name']


class FeatureSet(BaseModel):
    name = models.CharField(max_length=200)
    features = models.ManyToManyField(Feature)


class ProductManager(models.Manager):

    """ Product manager for product for table level operations """

    def get_products_from_cat(self, category):
        """ Gets products from category and child categories """
        if category is None:
            # TODO.prefetch_related('images', 'images__thumbnail_set')
            return self.get_queryset()
        cats = [x.pk for x in [category] + list(category.get_descendants())]
        # TODO.prefetch_related('images')
        return self.get_queryset().filter(enabled=True, categories__pk__in=cats)

    def recommended(self, category=None, num=3):
        return self.get_products_from_cat(category).order_by('?')[:num]

    def featured(self, category=None):
        # .order_by('?')
        return self.get_products_from_cat(category).filter(featured=True)


class VirtualProductVariant(Item):
    sku = None
    pk = None
    name = None
    product = None
    attributes = {}

    def get_price_per_item(self, discounts=None, **kwargs):
        return self.product.get_price_per_item(discounts, **kwargs)

    def get_price_with_discount(self, discounts=None):
        return self.product.get_price_with_discount(discounts)

    def display_product(self, attributes=None):
        return '%s' % (smart_text(self.product))

    def get_stock_quantity(self):
        # TODO
        return 100

    def __str__(self):
        return self.product.__str__()

    def get_absolute_url(self):
        return self.product.get_absolute_url()


class Product(BaseModel,  saleor_models.Product):
    objects = ProductManager()
    enabled = models.BooleanField(_("Enabled"), default=True)
    featured = models.BooleanField(_("Featured"), default=False)  # Destacado
    features = models.ManyToManyField(Feature, through='ProductFeatureValue')
    order = models.SmallIntegerField(_("Order"), default=10)
    weight = 0  # Para simular peso
    # Referencia producto
    sku = models.CharField("Referencia", max_length=80, default=' ')

    discounts = None
    discounted_price = None

    class Meta(BaseModel.Meta):
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['order']

    def get_slug(self):
        return slugify(self.name)

    def get_features(self):
        return ProductFeatureValue.objects.filter(product=self).select_related('feature')

    def get_price_with_discount(self, discounts=None):
        """Devuelve el precio con descuento cuando no se usan variantes de producto"""
        if self.discounted_price is not None:
            # Devolver precio con descuento previamente calculado
            return self.discounted_price
        price = self.price
        # Listado de objetos descuentos que aplican a este prod
        self.discounts = []
        if discounts:
            # TODO de momento  solo se permite solo un descuento
            for discount in discounts:
                try:
                    discount_value = discount.check_product(self)
                    # Si no hubo excepcion el descuento se puede aplicar
                    price -= discount_value
                    self.discounts.append(discount)
                    self.discounted_price = price
                    # Se devuelve pues solo se puede aplicar un descuento
                    return price
                except:
                    pass  # Descuento no aplicable

        return price

    def get_price_per_item(self, discounts=None):
        """Necesario cuando hay productos y no variantes en el carrito para 
        poder obtener el precio con los descuentos aplicados"""
        return self.get_price_with_discount(discounts)

    def get_virtual_variant(self):
        variant = VirtualProductVariant()
        variant.product = self.product
        variant.pk = self.product.pk
        variant.name = self.product.name
        variant.sku = self.product.sku
        return variant

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.get_slug(),
                                                 'pk': self.id})


class ProductFeatureValue(BaseModel):
    product = models.ForeignKey(Product)
    feature = models.ForeignKey(Feature, verbose_name=_("Feature"))
    value = models.CharField(_("Value"), max_length=200)
    order = models.SmallIntegerField(_("Order"), default=0)

    def __unicode__(self):
        return "%s: %s" % (self.feature.name, self.value)

    class Meta(BaseModel.Meta):
        verbose_name = _('Product Feature')  # 'Caracteristica de producto'
        # 'Caracteristicas de productos'
        verbose_name_plural = _('Product Features')
