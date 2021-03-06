from django.conf.urls import url

from .core import load_checkout
from . import views


urlpatterns = [
    url(r'^$', load_checkout(views.index_view), name='index'),
    url(r'^shipping-address/', load_checkout(views.shipping_address_view),
        name='shipping-address'),
    url(r'^shipping-method/', load_checkout(views.shipping_method_view),
        name='shipping-method'),
    url(r'^summary/', load_checkout(views.summary_view), name='summary')
]
