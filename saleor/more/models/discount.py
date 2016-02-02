# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.encoding import python_2_unicode_compatible
from django_prices.models import PriceField
from prices import FixedDiscount, Price
from saleor.product.models import Product
from saleor.product.models.discounts import NotApplicable
from saleor.more.models.common import BaseModel
from saleor.product.models import Category


class RuleBasedDiscount(BaseModel):

    """Clase base abstracta para crear modelos de descuento basados en reglas para aplicar el descuento.
    Los descuentos basados en reglas heredan de esta.

    - Se puede definir el descuento como valor fijo o porcentaje.
    - Se puede establecer que el descuento solo se aplique si el usuario ingresa un cupón
    - Se puede definir la fecha inicial y final donde el descuento es válido

    Las reglas que se definen pueden ser reglas para aplicar descuentos a productos del catalogo
    (ver CatalogDiscount y CatalogDiscountRule) o reglas que aplican descuentos a un carrito de compras.
    """

    name = models.CharField("Nombre", max_length=255)
    """Nombre"""
    description = models.TextField("Descripción")
    # products =  None #models.ManyToManyField(Product, blank=True)
    discount = models.IntegerField("Descuento")
    """Valor nominal del descuento"""
    discount_unit = models.SmallIntegerField(
        "Unidad de descuento", default=1, choices=((1, 'Valor fijo'), (2, 'Porcentaje')))
    """Unidad del descuento (valor fijo o porcentaje)"""

    activated_by_coupon = models.BooleanField(
        "Activado con cupón", default=False)
    """El descuento solo se aplica si se activa ingresando el coupon en la vista del carrito"""
    coupon = models.CharField("Cupon", max_length=50, null=True, blank=True)
    """Codigo del cupón"""
    date_from = models.DateField("Fecha inicio")
    date_to = models.DateField("Fecha fin")
    """Fecha inicio y final donde aplica el descuento"""

    enabled = models.BooleanField("Habilitado", default=False)
    """Si esta habilitado o no el descuento"""

    priority = models.SmallIntegerField("Prioridad", default=0)
    """Prioridad del descuento. Para cuando hay varios descuentos"""

 
    # TODO A futuro lo siguiente:
    """
    user: Especificar un usuario el cual sera el unico que pueda aplicar el cupón si se define
    coupon_qty: Cantidad de cupónes disponibles
    """

    def __repr__(self):
        return 'RuleBasedProductDiscount(name=%r, discount=%r, percent=%s)' % (
            self.name, str(self.discount), 'Yes' if self.discount_unit == 2 else 'No')

    def __unicode__(self):
        return self.name


    class Meta:
        abstract = True


class CatalogDiscount(RuleBasedDiscount):

    """Descuentos de catalogo que aplican rebajas a los precios de los productos en el catalogo que 
    pasan las reglas de descuento (CatalogDiscountRule).
    Funciona de dos maneras:
    1. Si este descuento esta habilitado y no se activa mediante cupón entonces el descuento
    se aplica directamente en el catalogo y muestra los precios descontados en la vista producto.
    Ej: Descuento del 20% para todas las guadañadoras STIHL.

    2. Si se especifica cupón entonces cuando  el usuario ingrese el cupón este descuento aplicara a LOCALE_PATHS
    productos del carrito que pasen las reglas de este descuento. Es lo mismo que 1 pero solo se activa cuando 
    se ingresa el cupón.
    Ej: Descuento del 20% para todas las guadañadoras STIHL ingresando el cupón DESCUENTOSTIHL
    """

    def check_product(self, product):
        """Chequea el producto  aplicandole todas las reglas de este descuento.
        Si supera las reglas se calcula el descuento.
        """
        b = True
        for i, rule in enumerate(list(self.rules.all())):
            if i == 0: #La primer regla siempre se agrega con un and
                b = b and rule.check_product(product)
            else:
                if rule.use_or:
                    b = b or rule.check_product(product) 
                else:
                    b = b and rule.check_product(product) 

        if not b:
            raise NotApplicable('El producto no ha superado las reglas para aplicar este descuento')
        # Obtener descuento
        price = product.price
        discount = price * self.discount / 100 if self.discount_unit == 2 else Price(self.discount, currency=settings.DEFAULT_CURRENCY)
        discount = discount.quantize(1) # para redondear el obj Price
        if discount > price:
            raise NotApplicable('El descuento es mayor al precio del producto. No se puede aplicar')
        return discount

    def explain_rules(self):
        """Devuelve string que explica las reglas"""
        rules = self.rules.all()
        out= []
        for i, r in enumerate(list(rules)):
            if i: #no se tiene en cuenta conector en regla 1
                con = '<b>Ó</b>' if r.use_or else '<b>y</b>'
                out.append(con)
            out.append("%s"%(r))
        return ' '.join(out)

    class Meta:
        verbose_name = u'Descuento de catálogo' 
        verbose_name_plural = u'Descuentos de catálogo' 

class CatalogDiscountRule(BaseModel):

    """Reglas aplicables para descuentos de catalogo. 
    (CatalogDiscount has_many CatalogDiscountRule)
    - Se puede configurar para validar que el producto pertenezca a una categoria. Tipo 1
    - Se puede configurar para validar que el producto sea un producto en especifico. Tipo 2
    por ej: rule.rtype = 1 , rule.category = Category(pk=10) # Regla que aprueba
    productos que pertenecen a la categoria pk=10
    """

    rtype = models.IntegerField(
        "Tipo", choices=((1, 'Categoria'), (2, 'Producto')))
    discount = models.ForeignKey(CatalogDiscount, related_name='rules')
    category = models.ForeignKey(Category, null=True, blank=True)
    product = models.ForeignKey(Product, null=True, blank=True)
    use_or = models.BooleanField("Ó", default=False)

    def check_product(self, product):
        """Testea que el producto pase esta regla"""
        if self.rtype == 1:
            # Categoria
            if product.category == self.category or product.category.parent == self.category:
                return True
        elif self.rtype == 2:
            # Producto
            if product.product_ptr == self.product:
                return True
        return False

    def __unicode__(self):
        entity = (u'Categoría', u'Producto')
        obj = self.category  if self.rtype == 1 else self.product
        return "%s = %s " %(entity[self.rtype-1], obj)
    class Meta:
        verbose_name = u'Regla de catálogo'
        verbose_name_plural = u'Reglas de catálogo'

# TODO EStos dos se harán a futuro
class CartDiscount(RuleBasedDiscount):

    """Descuentos que se aplican al total del carrito de compras como un descuento gral o envio gratis (free shipping).
   El descuento en este caso es uno solo y no por producto y las reglas que se definen se aplican al carrito como un todo."""
    # TODO
    pass


class CartDiscountRule(BaseModel):
    # TODO
    pass
