from rest_framework.permissions import BasePermission

from companies import models as companies_models


class IsCompanyAdmin(BasePermission):
    """ Permission class for checking whether the requesting user is admin of the company """

    def has_permission(self, request, view):
        company_id = view.kwargs['company_id']
        user = request.user

        is_company_admin = companies_models.Employee.objects.filter(
            user=user,
            company=company_id,
            is_company_admin=True
        ).exists()

        return is_company_admin


class IsCompanyVerified(BasePermission):
    """ Permission class for checking whether the company is verified or not """

    def has_permission(self, request, view):
        company_id = view.kwargs['company_id']
        is_company_verified = companies_models.Company.objects.filter(
            pk=company_id,
            is_verified=True
        ).exists()
        return is_company_verified
