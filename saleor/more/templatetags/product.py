from django import template
from prices import  Price
from django.conf import settings

register = template.Library()


@register.filter
def discounted_price(product, discounts):
    """Para obtener el precio del producto con el descuento aplicado
    :param discounts: Descuentos activos en el sistema.
    """
    # TODO descuento para producto  sin variantes!.
    return product.get_price_with_discount(discounts=discounts).net

@register.filter
def price_difference(price1, price2):
    """Para obtener el valor del descuento por producto.
    :param price1: precio del producto
    :param price2: precio del producto con el descuento
    """
    discount_val = (price1 - price2).net
    return discount_val if discount_val > Price(0, currency=settings.DEFAULT_CURRENCY) else ''


