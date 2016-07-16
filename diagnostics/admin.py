from django.contrib import admin

from diagnostics.models import TestQuestion, TestAnswer, TestResult, TestResultSolution

class TestAnswerInline(admin.TabularInline):
    model = TestAnswer

class TestQuestionAdmin(admin.ModelAdmin):
    inlines = [
        TestAnswerInline,
    ]
    
admin.site.register(TestQuestion, TestQuestionAdmin)

class TestResultSolutionInline(admin.TabularInline):
    model = TestResultSolution

class TestResultAdmin(admin.ModelAdmin):
    inlines = [
        TestResultSolutionInline,
    ]
    
admin.site.register(TestResult, TestResultAdmin)
