from django.contrib import admin

from commons.admin import CommonAdmin
from companies import models as companies_modals
from surveys import models as surveys_modals


# Company Admin
class EmployeeInlines(admin.TabularInline):
    model = companies_modals.Employee
    fields = ('user', 'is_company_admin')
    ordering = ('-updated_at',)
    extra = 0


class CompanyAdmin(CommonAdmin):
    list_filter = ('is_verified', 'city', 'state', 'is_active')
    list_display = ('name', 'employees', 'is_verified', 'is_active')
    search_fields = ('name', 'address', 'state', 'city')
    ordering = ('-updated_at',)
    inlines = (EmployeeInlines,)

    def employees(self, obj):
        """ return the count of the active employees of the company. """
        return obj.employees.filter(is_active=True, user__is_active=True).count()


admin.site.register(companies_modals.Company, CompanyAdmin)


# Company Questionnaires
@admin.register(companies_modals.CompanyQuestionnaire)
class CompanyQuestionnaireAdmin(CommonAdmin):
    list_display = ('company', 'questionnaire', 'is_active')
    list_filter = ('company', 'questionnaire', 'is_active')
    search_fields = ('company', 'questionnaire', 'is_active')
    ordering = ('-updated_at',)


# Questionnaire Rule
@admin.register(companies_modals.QuestionnaireRule)
class QuestionnaireRuleAdmin(CommonAdmin):
    list_display = (
        'company', 'questionnaire', 'rule_type', 'notification', 'is_active'
    )
    list_filter = ('rule_type', 'is_active')
    ordering = ('-updated_at',)

    def company(self, obj):
        """ return the name of the company. """
        return obj.company_questionnaire.company.name

    def questionnaire(self, obj):
        """ return the questionnaire title, """
        return obj.company_questionnaire.questionnaire.title


# Company Invites
@admin.register(companies_modals.CompanyInvite)
class CompanyInviteAdmin(CommonAdmin):
    list_display = ('company', 'receiver', 'status', 'is_active')
    list_filter = ('company', 'status', 'is_active')
    search_fields = ('company__name', 'receiver__first_name',)
    ordering = ('-updated_at',)


# Company Advices
@admin.register(companies_modals.CompanyAdvice)
class CompanyAdviceAdmin(CommonAdmin):
    list_display = ('company', 'advice_content', 'is_active')
    list_filter = ('company__name', 'is_active')
    ordering = ('-updated_at',)

    def company(self, obj):
        """ returns company name """
        return obj.company.name

    def advice_content(self, obj):
        """ return first 20 characters of advice. """
        return obj.text[:20]
