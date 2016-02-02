from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from views import CatalogView, ProductDetail, CartView, LoginView, ChangePersonalDataView, MyOrdersListView, \
    PasswordResetView, SetPasswordView, SetPasswordCompleteView
from saleor.checkout.urls import urlpatterns as checkout_urls
from web_shop.views.checkout import CheckoutView
from web_shop.views.order import OrderDetailView

TOKEN_PATTERN = ('(?P<token>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}'
                 '-[0-9a-z]{12})')
urlpatterns = patterns('',
    url(r'images/', include('django_images.urls')),
    url(r'^producto/(?P<slug>[-_\w]+)/(?P<pk>[0-9]{1,5})', ProductDetail.as_view(), name='product_detail'),
    # Order
    url(r'order/%s/' % (TOKEN_PATTERN), OrderDetailView.as_view(), name='order_details'),
    url(r'^(?P<slug>[-_\w]+)/(?P<cat_id>[0-9]{1,5})', CatalogView.as_view(), name='catalog'),
    url(r'productos/', CatalogView.as_view(), name='catalog-root'),
    url(r'carrito', CartView.as_view(), name='view_cart'),
    # Checkout
    url(r'checkout/(?P<step>[a-z0-9-]+)/$', CheckoutView.as_view(), name='checkout_details'),
    url(r'checkout', CheckoutView.as_view(step=None), name='checkout_index'),
    url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^logout$', LoginView.as_view(), name='logout'),
    url(r'^account_settings$', ChangePersonalDataView.as_view(), name='account_settings'),
    url(r'^request_email$', PasswordResetView.as_view(), name='request_email'),
    url(r'^set_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        SetPasswordView.as_view(), name='set_password'),
    url(r'^set_password_complete$', SetPasswordCompleteView.as_view(), name='set_password_complete'),
    url(r'^mis_compras', MyOrdersListView.as_view(), name='orders_history')
)
