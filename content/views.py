from django.shortcuts import render
from django.views.generic.base import TemplateView

from content.models import Item

class ItemView(TemplateView):
    template_name = "content/item.html"

    def get_context_data(self, **kwargs):
        context = super(ItemView, self).get_context_data(**kwargs)
        context['item'] = Item.objects.first()
        #TODO: render me properly
        return context
