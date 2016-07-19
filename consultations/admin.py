# -*- coding: utf-8 -*-

from django.contrib import admin

from consultations.models import FAQ, Consultation, Consultant

admin.site.register(FAQ)

class IsAnsweredFilter(admin.SimpleListFilter):
    title = u'Статус консультаций'

    parameter_name = 'is_answered'

    def lookups(self, request, model_admin):
        return (
            ('not_answered', u'Новые'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'not_answered':
            return queryset.filter(is_answered=False)
            
class ConsultationAdmin(admin.ModelAdmin):
    exclude = ('is_answered','answered_consultant', 'notification_sent_at', 'answer_sent_at')
    readonly_fields = ('created_at', 'answered_datetime')
    list_filter = (IsAnsweredFilter, )

admin.site.register(Consultation, ConsultationAdmin)
admin.site.register(Consultant)
