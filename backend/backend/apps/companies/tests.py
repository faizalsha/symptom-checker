from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from ddf import G
from rest_framework.test import APITestCase

from companies.serializers import CompanyInviteSerializer
from companies.models import Company, Employee, CompanyInvite

AUTH_USER = get_user_model()


# class CompanyInviteSerializerTest(TestCase):
#     def test_serializer_fk(self):
#         company = G(Company)
#         data = {
#             'receiver_email': 'john@gmail.com',
#             'first_name': 'John',
#             'company': company.id
#         }

#         serializer = CompanyInviteSerializer(data=data)
#         self.assertTrue(serializer.is_valid())
#         serializer.save()
#         self.assertTrue(AUTH_USER.objects.filter(
#             email='john@gmail.com').exists()
#         )

#     def test_user_invite(self):
#         receiver = G(AUTH_USER, email='a@b.com')
#         admin = G(AUTH_USER)
#         company = G(Company)
#         employee = G(Employee, user=admin,
#                      is_company_admin=True, company=company)
#         data = {
#             'receiver_email': receiver.email,
#             'company': company.id,
#             'first_name': 'john',
#             'last_name': 'smith'
#         }
#         serializer = CompanyInviteSerializer(data=data)

#         self.assertTrue(serializer.is_valid())

#         self.assertTrue(serializer.is_valid())
#         serializer.save()

#         qs = CompanyInvite.objects.filter(
#             receiver=receiver, company=company.id)

#         print(CompanyInvite.objects.all())

#         self.assertTrue(qs.exists())
#         self.assertEqual(len(qs), 1)
#         invite = qs.get(receiver=receiver)
#         self.assertEqual(invite.company, company)
#         self.assertEqual(invite.receiver, receiver)
#         self.assertEqual(invite.first_name, 'john')
#         self.assertEqual(invite.last_name, 'smith')

class CompanyInviteAPITest(APITestCase):
    def test_company_invite(self):
        url = reverse('companies:company-invite')
        print(url)
