from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from consultations.views import ConsultView, ConsultAnswerView, Consut2FAQView

urlpatterns = [
    url(r'^$', csrf_exempt(ConsultView.as_view())),
    url(r'^(?P<id>\d+)/$', csrf_exempt(ConsultAnswerView.as_view())),
    url(r'^(?P<id>\d+)/2faq/', csrf_exempt(Consut2FAQView.as_view())),
]
