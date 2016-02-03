# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from satchless.item import Partitioner
from saleor.cart import Cart
from saleor.cart.forms import ReplaceCartLineFormSet
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from saleor.more.models import CatalogDiscount
from datetime import datetime as dt
from django.template.response import TemplateResponse

class CartView(TemplateView):
    template_name = 'more/cart/cart.html'
    cart, formset = None, None
    
    def get(self, request, *args, **kwargs):
        """ Actualiza el descuento de cupon usado segun los parametros pasados por GET.
            Si 'num_items' devuelve el numero de items (para clientes ajax)
            Si 'del_coupon' se borra el cupon actual.
            Si 'coupon' se verifica que exista y esté activo y se agrega
            al listado de descuentos.
        """

        if 'num_items' in request.GET:
            return TemplateResponse(request, 'web_shop/cart_num_items.html', context={})
        elif 'del_coupon' in request.GET:
            try:
                del request.session['coupon']
            except: pass
            # Redireccionar para que el middleware de descuentos se vuelva a ejecutar
            return self.redirect_to_cart()

        elif 'coupon' in request.GET and len(request.GET['coupon'].strip()):
            coupon = request.GET['coupon']
            dqset = CatalogDiscount.objects.prefetch_related('rules')\
                                           .filter(request.coupon_query, coupon=coupon)[:1]
            # Almacenar datos del descuento de cupon encontrado en la sesion
            if len(dqset):
                request.session['coupon'] = {'name': coupon, 'description': dqset[0].description}
                request.discounts = request.discounts | dqset #Agregarlo al queryset
            else:
                messages.error(request, "El cupón ingresado no es válido o no está activo")
                pass

        return super(CartView, self).get(request, *args, **kwargs)

    
    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        request = self.request
        cart = Cart.for_session_cart(request.cart, discounts=request.discounts)
        formset = ReplaceCartLineFormSet( request.POST or None,
                                     cart=cart)

        cart_partitioner = Partitioner(cart)
        context['cart'] = cart_partitioner
        context['formset'] = formset

        # Calcular descuentos para todos los productos
        for cartline in cart:
            cartline.product.get_price_with_discount(self.request.discounts)

        return context


    def post(self, request, *args, **kwargs):
        cart = Cart.for_session_cart(request.cart, discounts=request.discounts)

        try:
            formset = ReplaceCartLineFormSet(request.POST or None,
                                         cart=cart)
            if formset.is_valid():
                msg = _('Se ha actualizado la cantidad de productos.')
                messages.success(request, msg)
                formset.save()
            else:
                msg = _('Error. No hay suficientes articulos en inventario.')
                messages.error(request, msg)
        except Exception, e:
            msg = _('Error. No se puede actualizar la cantidad.')
            print "Error", e
            messages.error(request, msg)
               
        self.cart = cart
        self.formset = formset

        if not len(cart):
            #Quitar todos los cupones de descuento si el carro se vació
            try:
                del request.session['coupon']
            except: pass

        return self.redirect_to_cart()

    def redirect_to_cart(self):
        if 'popup' in self.request.GET:
            response =  redirect("view_cart")
            response['Location'] += '?popup=1'
            return response
        else:
            return redirect("view_cart")
        #return super(CartView, self).get(request, *args, **kwargs)
