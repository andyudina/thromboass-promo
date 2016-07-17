from django.conf.urls import url

from diagnostics.views import StartDiagnosticView, NextStepView, AnswerQuestionView

urlpatterns = [
    url(r'^start/$', StartDiagnosticView.as_view()),
    url(r'^next/$', NextStepView.as_view()),
    url(r'^questions/(?P<question_id>\d+)/', AnswerQuestionView.as_view()),
]