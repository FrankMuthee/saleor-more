from saleor.more.models import CatalogDiscount
from datetime import datetime as dt
from saleor.cart import Cart
from django.db.models import Q


class DiscountMiddleware:

    def process_request(self, request):
        """Carga a request los descuentos habilitados y que estan vigentes segun las fechas"""
        
        today = dt.today()
        #Verificar si el usuario tiene activo descuentos activados con cupon
        request.coupon_query = Q(enabled=True, activated_by_coupon=True,
                date_from__lte=today, date_to__gte=today)

        if 'coupon' in request.session:
            coupon = request.session['coupon']['name']
            dqset = CatalogDiscount.objects.prefetch_related('rules').filter(request.coupon_query, coupon=coupon).order_by('priority')
        else:
            dqset = CatalogDiscount.objects.prefetch_related('rules').none()
 
        discounts = CatalogDiscount.objects.filter(enabled=True,
                                                   activated_by_coupon=False,
                                                   date_from__lte=today,
                                                   date_to__gte=today).prefetch_related('rules').order_by('priority') | dqset 
        # El "| dqset"  hace un UNION entre los dos querysets

        request.discounts = discounts

    def process_template_response(self, request, response):
        # calcular el total de articulos en el carrito
        total = 0
        cart = Cart.for_session_cart(request.cart)
        for cartline in cart:
            total = total + cartline.get_quantity()
        response.context_data['total_units'] = total

        return response
