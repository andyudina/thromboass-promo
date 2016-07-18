from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from diagnostics.views import StartDiagnosticView, NextStepView, AnswerQuestionView, DiagnosticView, PreviousStepView

urlpatterns = [
    url(r'^start/$', csrf_exempt(StartDiagnosticView.as_view())),
    url(r'^next/$', NextStepView.as_view()),
    url(r'^prev/$', PreviousStepView.as_view()),
    url(r'^questions/(?P<question_id>\d+)/', csrf_exempt(AnswerQuestionView.as_view())),
    url(r'^$', DiagnosticView.as_view()),
]
