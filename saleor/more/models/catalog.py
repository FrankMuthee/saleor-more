from django.db import models
from saleor.product.models import Category
from common import BaseModel
from versatileimagefield.fields import VersatileImageField, PPOIField
from django.utils.html import mark_safe


class CategoryImage(BaseModel):
    category = models.ForeignKey(Category, related_name='images')
    image = VersatileImageField(
        upload_to='categories', ppoi_field='ppoi', blank=False)
    ppoi = PPOIField()

    class Meta(BaseModel.Meta):
        verbose_name = "Imagen"
        verbose_name_plural = "Imagen"
