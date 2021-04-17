from django.contrib import admin

from commons.admin import CommonAdmin
from surveys import models as surveys_models


# Questionnaire Admin
class TipInline(admin.TabularInline):
    model = surveys_models.Tip
    extra = 0


@admin.register(surveys_models.Questionnaire)
class QuestionnaireAdmin(CommonAdmin):
    readonly_fields = ('published_on',)
    list_display = ('title', 'description', 'is_published', 'published_on')
    list_filter = ('is_published', 'is_active', 'published_on')
    search_fields = ('title', 'description', 'published_on', 'created_on')
    ordering = ('-updated_at',)
    inlines = (TipInline, )

    def description(self, obj):
        """ returns first 20 characters of description. """
        return obj.description[:20]


# Question Admin
class ChoiceInline(admin.StackedInline):
    model = surveys_models.Choice
    extra = 0


@admin.register(surveys_models.Question)
class QuestionAdmin(CommonAdmin):
    list_display = ('question', 'question_type', 'is_active')
    list_filter = ('question_type', 'is_active')
    search_fields = ('text', 'choices__text')
    ordering = ('-updated_at',)
    inlines = (ChoiceInline,)

    def question(self, obj):
        """ returns question's text's first 20 characters. """
        return obj.text[:20]


# QuestionnaireResponse Admin
@admin.register(surveys_models.QuestionnaireResponse)
class QuestionnaireResponseAdmin(CommonAdmin):
    list_display = ('questionnaire', 'user', 'score', )
    list_filter = ('user', 'questionnaire', 'score',)
    search_fields = (
        'user__name', 'questionnaire__title', 'questionnaire_description', 'score'
    )
    ordering = ('-updated_at',)
    readonly_fields = (
        'user', 'company', 'questionnaire',
        'risk_level', 'score', 'updated_at', 'created_at'
    )
