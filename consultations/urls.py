from django.conf.urls import url

from consultation.views import ConsultView, ConsultUpdateView, Consut2FAQView

urlpatterns = [
    url(r'^$', ConsultView.as_view()),
    url(r'^(?P<id>\d+)/$', ConsultAnswerView.as_view()),
    url(r'^(?P<id>\d+)/2faq/', Consut2FAQView.as_view()),
]
