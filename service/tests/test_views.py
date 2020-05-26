import datetime
from decimal import Decimal

from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase

from service.models import Partner, Client, Measurement, Meeting, Plan, PAL


USER = {'username': 'user', 'password': 'user1234'}
MODELS = ['partner', 'client', 'measurement', 'meeting', 'plan']


class LoginRequiredTest(TestCase):
    URLS = [
        # List views
        'partners/',
        'clients/',
        'measures/',
        'meetings/',
        'plans/',
        # Detail views
        'partner/1',
        'client/1',
        # 'measure/1',
        'meeting/1',
        'plan/1',
        # Form views
        'partner/create/',
        'partner/1/update/',
        'client/create/',
        'client/1/update/',
        'measure/create/',
        'measure/1/update/',
        'meeting/create/',
        'meeting/1/update/',
        'plan/create/',
        'plan/1/update/',
        # Delete views
        'partner/1/delete/',
        'client/1/delete/',
        'measure/1/delete/',
        'meeting/1/delete/',
        'plan/1/delete/']

    @classmethod
    def setUpTestData(cls):
        create_one_of_each()

    def test_redirect_without_login(self):
        for url in self.URLS:
            response = self.client.get('/main/' + url)
            try:
                self.assertRedirects(response, '/accounts/login/?next=/main/' + url)
            except:
                print(f"FAILED: url '{url}'")
                self.assertRedirects(response, '/accounts/login/?next=/main/' + url)


class TemplateUsedTest(TestCase):
    TEMPLATE_URL_MAP = [
        # List views
        {'template': 'common/generic_list.html', 'urls': [
            'partners/',
            'clients/',
            'measures/',
            'meetings/',
            'plans/',
        ]},
        # Detail views
        {'template': 'common/generic_detail.html', 'urls': [
            'partner/1',
            # 'measure/1',
            'meeting/1',
            'plan/1',
        ]},
        {'template': 'service/client_detail.html', 'urls': [
            'client/1',
        ]},
        # Form views
        {'template': 'common/generic_form.html', 'urls': [
            'measure/create/',
            'measure/1/update/',
        ]},
        {'template': 'service/partner_form.html', 'urls': [
            'partner/create/',
            'partner/1/update/',
        ]},
        {'template': 'service/client_form.html', 'urls': [
            'client/create/',
            'client/1/update/',
        ]},
        {'template': 'service/meeting_form.html', 'urls': [
            'meeting/create/',
            'meeting/1/update/',
        ]},
        {'template': 'plan/index.html', 'urls': [
            'plan/create/',
            'plan/1/update/',
        ]},
        # Delete views
        {'template': 'common/generic_confirm_delete.html', 'urls': [
            'partner/1/delete/',
            'client/1/delete/',
            'measure/1/delete/',
            'plan/1/delete/',
        ]},
        {'template': 'service/meeting_confirm_delete.html', 'urls': [
            'meeting/1/delete/',
        ]}]

    @classmethod
    def setUpTestData(cls):
        create_one_of_each()

    def test_correct_template_used(self):
        self.client.login(**USER)
        for template in self.TEMPLATE_URL_MAP:
            for url in template['urls']:
                response = self.client.get('/main/' + url)
                try:
                    self.assertEqual(response.status_code, 200)
                    self.assertTemplateUsed(response, template['template'])
                except:
                    print(f"FAILED: template '{template['template']}', url '{url}'")
                    self.assertEqual(response.status_code, 200)
                    self.assertTemplateUsed(response, template['template'])


class EmptyDatabaseTest(TestCase):
    URLS = [
        # List views
        'partners/',
        'clients/',
        'measures/',
        'meetings/',
        'plans/',
        # Form views
        'partner/create/',
        'client/create/',
        'measure/create/',
        'meeting/create/',
        'plan/create/']

    @classmethod
    def setUpTestData(cls):
        create_nutritionist()

    def test_empty_database(self):
        self.client.login(**USER)
        for url in self.URLS:
            response = self.client.get('/main/' + url)
            try:
                self.assertEqual(response.status_code, 200)
            except:
                print(f"FAILED: url '{url}'")
                self.assertEqual(response.status_code, 200)


def create_one_of_each():
    user = create_nutritionist()
    partner = Partner.objects.create(name='partner', calendar='calendar')
    partner.save()
    client = Client.objects.create(
        nutritionist=user, name='client', gender='f', age=30, height=170,
        weight=Decimal(60.5), pal=PAL[1][0], partner=partner)
    client.save()
    measurement = Measurement.objects.create(
        client=client, measure='w', value=Decimal(62.3), date=datetime.date.today())
    meeting = Meeting.objects.create(
        client=client, date=datetime.date.today(), time=datetime.datetime.now().time(),
        duration=30, summary='summary', event='event')
    plan = Plan.objects.create(client=client)
    measurement.save()
    meeting.save()
    plan.save()
    return user

def create_nutritionist():
    user = User.objects.create_user(**USER)
    user.save()
    group = Group.objects.create(name='nutritionist')
    group.permissions.set([Permission.objects.get(codename=f'{perm}_{model}')
        for perm in ['view', 'add', 'change', 'delete'] for model in MODELS])
    group.user_set.add(user)
    group.save()
    return user
