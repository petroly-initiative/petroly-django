from django.test import TestCase, Client
from django.contrib.auth import get_user_model, get_user
from django.views.generic.edit import CreateView
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import json

from .models import Offer
from .views import OfferCreateView
from .views import *



class UserTestCase(TestCase):
    
    def setUp(self) -> None:
        self.user1 = get_user_model().objects.create_user(
            username='user-test1',
            email='test1@test.com',
            password='ekrlw32rlwr'
        )
        self.user1.status.verified = True
        self.user1.status.save()

        self.user2 = get_user_model().objects.create_user(
            username='user-test2',
            email='test2@test.com',
            password='fjw2309ekfwlwr',
        )

class OfferTestCase(UserTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.data1 = {
            'name': 'Ahmad',
            'phone': '094352345234',
            'email': 'ds@ad.com',
            'smoking': False,
            'staying_up': True,
            'sociable': True,
            'temperature': 'cold always',
            'hometown': 'Dhahran',
            'comment': 'People usually are the same\n but I\'m differnet.',
        }
        self.offer1 = Offer.objects.create(**self.data1, user=self.user1)

class OfferModelTestCase(OfferTestCase):
    '''Test the `Offer` model, and its fields.'''

    def setUp(self) -> None:
        super().setUp()

        self.data2 = {
            'name': 'Moh',
            'phone': '094354245234',
            'email': 'abc@ad.com',
            'smoking': True,
            'staying_up': False,
            'sociable': False,
            'temperature': 'not important',
            'hometown': '',
            'comment': '',
        }


    def test_get_offer(self):
        offer: Offer = Offer.objects.get(user=self.user1)
        for key, value in self.data1.items():
            self.assertEqual(offer.__getattribute__(key), value)
        self.assertEqual(offer.user, self.user1)

    def test_crud_offer(self):
        # Create an offer and change the user to `user2`
        offer: Offer = Offer(**self.data1)
        offer.user = self.user2
        offer.save()

        # Read and check populated data
        for key, value in self.data1.items():
            self.assertEqual(offer.__getattribute__(key), value)
        self.assertEqual(offer.user, self.user2)

        # Update
        offer = Offer.objects.get(user=self.user2)
        for key, value in self.data2.items():
            offer.__setattr__(key, value)
        offer.save()
        for key, value in self.data2.items():
            self.assertEqual(offer.__getattribute__(key), value)
        self.assertEqual(offer.user, self.user2)

        # Delete
        Offer.objects.get(user=self.user2).delete()
        with self.assertRaises(ObjectDoesNotExist):
            Offer.objects.get(user=self.user2)


class OfferViewTestCase(OfferTestCase):
    
    def setUp(self) -> None:
        super().setUp()
        self.client = Client()
        self.client.force_login(self.user2, settings.AUTHENTICATION_BACKENDS[1])

    def test_list_offer_view(self):
        response = self.client.get('/roommate/list/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.route, 'roommate/list/')
        self.assertEqual(len(response.context['offer_list']), 1)
        self.assertEqual(response.context['offer_list'][0], self.offer1)
        self.assertTemplateUsed(response, 'roommate/offer_list.html')
        self.assertEqual(response.resolver_match.app_name, 'roommate')
        self.assertEqual(response.resolver_match.url_name, 'offer_list')
        self.assertEqual(response.resolver_match.view_name, 'roommate:offer_list')
        self.assertEqual(response.resolver_match.func.__name__, OfferListView.as_view().__name__)

    def test_create_offer_view(self):
        # Open create view
        response = self.client.get('/roommate/create/')
        self.assertEqual(response.wsgi_request.user, self.user2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.route, 'roommate/create/')
        self.assertTemplateUsed(response, 'roommate/offer_form.html')
        self.assertEqual(response.resolver_match.view_name, 'roommate:offer_create')
        self.assertEqual(response.resolver_match.func.__name__, OfferCreateView.as_view().__name__)
        
        # Create an `Offer` object
        response = self.client.post('/roommate/create/', data=self.data1)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Offer.objects.get(user=self.user2))
        self.assertEqual(response.url, f'/roommate/update/{self.user2.offer.pk}')
        self.assertTemplateUsed('roommate/offer_form.html')
        self.assertEqual(response.resolver_match.func.__name__, OfferCreateView.as_view().__name__)
        
        # If a user has created an `Offer` object prevernt it to open `create`
        response = self.client.get('/roommate/create/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/roommate/update/{self.user2.offer.pk}')

    def test_update_offer_view(self):
        # Open update view
        response = self.client.get(f'/roommate/update/{self.user1.offer.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.route, 'roommate/update/<int:pk>')
        self.assertEqual(response.resolver_match.app_name, 'roommate')
        self.assertEqual(response.resolver_match.url_name, 'offer_update')
        self.assertEqual(response.resolver_match.view_name, 'roommate:offer_update')
        self.assertTemplateUsed(response, 'roommate/offer_form.html')
        self.assertEqual(response.context['offer'], self.user1.offer)
        self.assertEqual(response.resolver_match.func.__name__, OfferUpdateView.as_view().__name__)

        # Update an `Offer` object
        response = self.client.post(f'/roommate/update/{self.user1.offer.pk}', 
                        {'name': 'Khaled', 'staying_up': True, 
                        'use-default-email': '', 'email': 'new@fw.com'}
        )
        self.assertEqual(response.status_code, 302)
        offer = Offer.objects.get(user=self.user1)
        self.assertEqual(offer.name, 'Khaled')
        self.assertEqual(offer.staying_up, True)
        self.assertEqual(offer.email, self.user2.email)

    def test_delete_offer_view(self):
        user = get_user_model().objects.create_user(username='temp-user', password='rekmfwoeq')
        self.client.force_login(user, settings.AUTHENTICATION_BACKENDS[1])
        offer = Offer.objects.create(
            **self.data1,
            user=user
        )
        self.assertEqual(Offer.objects.get(user=user), offer)
        
        # Get delete an `Offer` page
        response = self.client.get(f'/roommate/delete/{offer.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.route, 'roommate/delete/<int:pk>')
        self.assertEqual(response.resolver_match.view_name, 'roommate:offer_delete')
        self.assertTemplateUsed(response, 'roommate/offer_confirm_delete.html')
        self.assertEqual(response.resolver_match.func.__name__, OfferDeleteView.as_view().__name__)

        # Confirm delete
        response = self.client.post(f'/roommate/delete/{offer.pk}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.resolver_match.route, 'roommate/delete/<int:pk>')
        self.assertEqual(response.resolver_match.view_name, 'roommate:offer_delete')
        self.assertTemplateNotUsed(response, 'roommate/offer_confirm_delete.html')
        self.assertEqual(response.resolver_match.func.__name__, OfferDeleteView.as_view().__name__)

        # Try get the deleted `Offer` object
        self.assertEqual(self.client.get(f'/roommate/delete/{offer.pk}').status_code, 404)
        with self.assertRaises(ObjectDoesNotExist):
            Offer.objects.get(user=user)

class OfferGraphQLTestCase(OfferTestCase):
    
    def setUp(self) -> None:
        super().setUp()
        self.client = Client()
        self.client.force_login(self.user1, settings.AUTHENTICATION_BACKENDS[1])



    def test_offers_query(self):
        offers_query = '''
        query Offers{
            offers(
                limit: 1
            ){
                data{
                id, name, phone, email,
                smoking, stayingUp, sociable, temperature, 
                hometown, comment,
                success,
                errors,
                }
            }
        }
        '''
        response = self.client.post('/endpoint/',
                        data={'query': offers_query})
        self.assertEqual(response.status_code, 200)
        
        json_data = json.loads(response.content)
        first_offer = json_data['data']['offers']['data'][0]

        self.assertEqual(first_offer['success'], True)
        self.assertEqual(int(first_offer['id']), self.offer1.pk)
        self.assertEqual(first_offer['name'], self.offer1.name)
        self.assertEqual(first_offer['name'], self.offer1.name)
        self.assertEqual(first_offer['phone'], self.offer1.phone)
        self.assertEqual(first_offer['email'], self.offer1.email)
        self.assertEqual(first_offer['smoking'], self.offer1.smoking)
        self.assertEqual(first_offer['stayingUp'], self.offer1.staying_up)
        self.assertEqual(first_offer['sociable'], self.offer1.sociable)
        self.assertEqual(first_offer['temperature'], self.offer1.temperature)
        self.assertEqual(first_offer['hometown'], self.offer1.hometown)
        self.assertEqual(first_offer['comment'], self.offer1.comment)

    def test_crud_offer(self):
        offer_create = '''
        mutation{
            offerCreate(
                input: {
                name: "name", email: "email@c.com",
                phone: "0123456789", 
                smoking: true, stayingUp: false, 
                sociable: false, temperature: "Hot",
                hometown: "Dhahran", comment:"Anyone.",
                }
            ){
                ok
                result{
                id
                }
            }
        }
        '''
        # A user trying to add two offers
        response = self.client.post('/endpoint/', data={'query': offer_create})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['errors'][0]['message'], 'You already have created an offer')

        # Updating an Offer object
        