from datetime import datetime
from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from management.models import Parking, ParkingSpace, Ticket

class ParkingTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="admin123")
        managers_group, _ = Group.objects.get_or_create(name="Manager")
        self.user.groups.add(managers_group)
        self.token = Token.objects.create(user_id=self.user.id)
        self.parking = Parking.objects.create(parking_name="New Parking", hour_price=4.0, created_by=self.user)
    
    def test_list_parking_lots(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('parking-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_parking_creation(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("parking-list")
        data = {
	        "parking_name": "Another Parking",
	        "hour_price": 6.0,
            "num_spaces": 20,
        }
        response = self.client.post(url ,data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Parking.objects.filter(parking_name='Another Parking').exists())
    
    def test_parking_reading(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("parking-detail", kwargs={'pk': self.parking.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Parking.objects.filter(parking_name='New Parking').exists())
        
    def test_parking_updating(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("parking-detail", kwargs={'pk': self.parking.pk})
        data = {
	        "parking_name": "Another Parking",
	        "hour_price": 7.0
        }
        response = self.client.put(url ,data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.parking.refresh_from_db()
        self.assertEqual(self.parking.hour_price, 7.0)
    
    def test_parking_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("parking-detail", kwargs={'pk': self.parking.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Parking.objects.filter(parking_name='New Parking').exists())


    def test_list_parking_spaces(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('parking-spaces-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ParkingSpaceTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="admin123")
        managers_group, _ = Group.objects.get_or_create(name="Manager")
        self.user.groups.add(managers_group)
        self.token = Token.objects.create(user_id=self.user.id)
        self.parking = Parking.objects.create(parking_name="New Parking", hour_price=4.0, created_by=self.user)
        self.parking_space = ParkingSpace.objects.create(cod="A01", status=False, parking=self.parking, created_by=self.user)
    
    def test_list_parking_spaces(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('parking-spaces-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_parking_space_creation(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("parking-spaces-list")
        data = {
	        "cod": "A02",
	        "status": False,
            "parking": self.parking.id
        }
        response = self.client.post(url ,data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ParkingSpace.objects.filter(cod='A02').exists())
    
    def test_parking_space_reading(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("parking-spaces-detail", kwargs={'pk': self.parking_space.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ParkingSpace.objects.filter(cod="A01").exists())
        
    def test_parking_space_updating(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("parking-spaces-detail", kwargs={'pk': self.parking_space.pk})
        data = {
	        "cod": "A02",
	        "status": True,
            "parking": self.parking.id
        }
        response = self.client.put(url ,data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.parking_space.refresh_from_db()
        self.assertEqual(self.parking_space.status, True)
    
    def test_parking_space_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("parking-spaces-detail", kwargs={'pk': self.parking_space.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ParkingSpace.objects.filter(cod='A01').exists())

    def test_list_available_spaces(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("reservation-list-available")
        response = self.client.get(url, {'parking_id': self.parking.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

class TicketTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="admin123")
        managers_group, _ = Group.objects.get_or_create(name="Manager")
        self.user.groups.add(managers_group)
        self.token = Token.objects.create(user_id=self.user.id)
        self.parking = Parking.objects.create(parking_name="New Parking", hour_price=4.0, created_by=self.user)
        self.parking_space = ParkingSpace.objects.create(cod="A01", status=False, parking=self.parking, created_by=self.user)
        self.ticket = Ticket.objects.create(
            model = "Jeep Renegade",
	        license_plate = "HJX8321",
	        checkin = "08:00:00",
	        checkout = "09:00:00",
	        parking_space = self.parking_space,
	        value = 0.0,
            created_by = self.user
        )
    
    def test_list_tickets(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('tickets-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_ticket_creation(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("tickets-list")
        data = {
	        "model": "Honda Civic",
	        "license_plate": "OWD7131",
	        "checkin": "09:00:00",
	        "checkout": "00:00:00",
	        "parking_space": self.parking_space.id,
	        "value": 0.0
        }
        response = self.client.post(url ,data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Ticket.objects.filter(license_plate="OWD7131").exists())
    
    def test_ticket_reading(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("tickets-detail", kwargs={'pk': self.ticket.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Ticket.objects.filter(license_plate="HJX8321").exists())
        
    def test_ticket_updating(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("tickets-detail", kwargs={'pk': self.ticket.pk})
        data = {
	        "model": "Honda Civic",
	        "license_plate": "OWD7131",
	        "checkin": "09:00:00",
	        "checkout": "11:00:00",
	        "parking_space": self.parking_space.id,
	        "value": 10.0
        }
        response = self.client.put(url ,data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.value, 10.0)
    
    def test_ticket_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("tickets-detail", kwargs={'pk': self.ticket.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ticket.objects.filter(license_plate='HJX8321').exists())

    def test_ticket_calculation(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse("tickets-calculateTicket", kwargs={'pk': self.ticket.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['value'], self.parking.hour_price)

class ReservationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="admin123")
        managers_group, _ = Group.objects.get_or_create(name="Manager")
        self.user.groups.add(managers_group)
        self.token = Token.objects.create(user=self.user)
        self.parking = Parking.objects.create(parking_name="New Parking", hour_price=4.0, created_by=self.user)
        self.parking_space = ParkingSpace.objects.create(cod="A01", status=False, parking=self.parking, created_by=self.user)

    def test_unavailable_parking_space(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = '/api/reservations/'
        # Dados para criar uma reserva com a mesma vaga de estacionamento e período de tempo
        data = {
            'parking_space': self.parking_space.id,
            'checkin': '2024-04-25T13:00',
            'checkout': '2024-04-25T16:00',
            'created_by': self.user.id,  
        }
        # Cria uma reserva para o mesmo espaço de estacionamento e o mesmo período de tempo
        self.client.post(url, data)
        # Tenta criar a mesma reserva novamente
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    

