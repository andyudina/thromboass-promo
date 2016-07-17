from django.conf.urls import url

from consultations.views import ConsultView, ConsultAnswerView, Consut2FAQView

urlpatterns = [
    url(r'^$', ConsultView.as_view()),
    url(r'^(?P<id>\d+)/$', ConsultAnswerView.as_view()),
    url(r'^(?P<id>\d+)/2faq/', Consut2FAQView.as_view()),
]
