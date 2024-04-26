from datetime import datetime
from jsonschema import ValidationError
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotAuthenticated, PermissionDenied

from core.permissions import IsManager, IsEmployee
from management.models import Parking, ParkingSpace, Ticket, Reservation
from management.api.serializers import ParkingSerializer, ParkingSpaceSerializer, TicketSerializer, ReservationSerializer
from management.services import ParkingService, ParkingSpaceService, TicketService

class ParkingViewSet(ModelViewSet):
    serializer_class = ParkingSerializer
    queryset = Parking.objects.all()
    permission_classes = [IsManager]
    service = ParkingService()

    def create(self, request, *args, **kwargs):
        serializer = ParkingSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            new_parking = self.service.create(serializer, request.user)
            serializer = ParkingSerializer(new_parking)
            return Response(
                {"Info": "Parking created!", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except (ParseError, ValueError):
            return Response(
                {
                    "Info": "Fail to create new parking!"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PermissionDenied:
            return Response(
                {"Info": "Permission Denied."}, status=status.HTTP_403_FORBIDDEN
            )
        except NotAuthenticated:
            return Response(
                {"Info": "Not Authenticated User."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

class ParkingSpaceViewSet(ModelViewSet):
    serializer_class = ParkingSpaceSerializer
    queryset = ParkingSpace.objects.all()
    permission_classes = [IsEmployee | IsManager]
    service = ParkingSpaceService()

    def create(self, request, *args, **kwargs):
        serializer = ParkingSpaceSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            new_parking_space = self.service.create(serializer, request.user)
            serializer = ParkingSpaceSerializer(new_parking_space)
            return Response(
                {"Info": "Parking space created!", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except (ParseError, ValueError):
            return Response(
                {
                    "Info": "Fail to create new parking space!"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PermissionDenied:
            return Response(
                {"Info": "Permission Denied."}, status=status.HTTP_403_FORBIDDEN
            )
        except NotAuthenticated:
            return Response(
                {"Info": "Not Authenticated User."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
    @action(detail=False, methods=['get'], url_path='list-available', name='list-available')
    def list_available_spaces(self, request):
        parking_id = request.query_params.get('parking_id')

        try:
            parking = Parking.objects.get(id=parking_id)
            parking_spaces = parking.spaces.all()
            serializer = ParkingSpaceSerializer(parking_spaces, many=True)
            available_spaces = []

            for space_data in serializer.data:
                space_id = space_data['id']
                is_available = ParkingSpace.objects.get(pk=space_id).status
                space_data['is_available'] = is_available
                available_spaces.append(space_data)

            return Response({"info": "Lista de vagas disponíveis no momento", "data": available_spaces}, status=status.HTTP_200_OK)

        except Parking.DoesNotExist:
            return Response({"error": "Estacionamento não encontrado.Tente novamente!"}, status=status.HTTP_404_NOT_FOUND)

class TicketViewSet(ModelViewSet):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()
    permission_classes = [IsEmployee | IsManager]
    service = TicketService()

    def create(self, request, *args, **kwargs):
        serializer = TicketSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            new_ticket = self.service.create(serializer, request.user)
            serializer = TicketSerializer(new_ticket)
            return Response(
                {"Info": "Ticket created!", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except (ParseError, ValueError):
            return Response(
                {
                    "Info": "Fail to create new ticket!"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PermissionDenied:
            return Response(
                {"Info": "Permission Denied."}, status=status.HTTP_403_FORBIDDEN
            )
        except NotAuthenticated:
            return Response(
                {"Info": "Not Authenticated User."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(methods=['get'],detail=True, url_path="payment")
    def calculateTicket(self, request, pk):
        try:
            ticket = self.get_object()
            updated_ticket = self.service.calc_ticket(ticket)
            serializer = TicketSerializer(updated_ticket)
            return Response(
                {"Info": "Ticket checkout!", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Ticket.DoesNotExist:
            return Response(
                {
                    "Info": "Fail to calculate Ticket!"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except NotAuthenticated:
            return Response(
                {"Info": "Not Authenticated User."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except PermissionDenied:
            return Response(
                {"Info": "Permission Denied."}, status=status.HTTP_403_FORBIDDEN
            )
        
class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parking_space_id = serializer.validated_data.get('parking_space')
        checkin = serializer.validated_data.get('checkin')
        checkout = serializer.validated_data.get('checkout')

        if not checkin or not checkout:
            raise ValidationError('O checkin e checkout são campos obrigatórios.')

        if not self.is_space_available(parking_space_id, checkin, checkout):
            return Response({'error': 'Não há vaga disponível para o período informado.'}, status=status.HTTP_400_BAD_REQUEST)

        reservation = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def is_space_available(self, parking_space_id, checkin, checkout, current_reservation_id=None):
        # Verifica se já há reservas para este espaço de estacionamento durante o período especificado
        overlapping_reservations = Reservation.objects.filter(
            parking_space_id=parking_space_id,
            checkin__lt=checkout,
            checkout__gt=checkin
        ).exclude(id=current_reservation_id).exists()
        # Se houver reservas sobrepostas, a vaga não está disponível
        return not overlapping_reservations