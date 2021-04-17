from django_filters import rest_framework as filters

from surveys.models import QuestionResponse, Question


class QuestionFilters(filters.FilterSet):
    """ FilterSet class for filtering Questions based on Questionnaire. """
    class Meta:
        model = Question
        fields = (
            'questionnaire',
        )


class QuestionResponseFilters(filters.FilterSet):
    """ FilterSet class for filtering Question responses based on questionnaire response. """
    class Meta:
        model = QuestionResponse
        fields = (
            'questionnaire_response',
        )
