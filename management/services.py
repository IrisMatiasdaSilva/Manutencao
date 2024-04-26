from datetime import datetime
from management.models import Parking, ParkingSpace, Ticket

class ParkingService:

    def create(self, serializer, user):
        new_parking = Parking.objects.create(
                parking_name = serializer.validated_data['parking_name'],
                hour_price = serializer.validated_data['hour_price'],
                created_by = user,
            )
        num_spaces = serializer.validated_data['num_spaces']
        for i in range(1,num_spaces):
            temp_parking_space = ParkingSpace.objects.create(
                cod = "A"+str(i),
                status = False,
                parking = new_parking,
                created_by = user,
            )
        return new_parking

class ParkingSpaceService:

    def create(self, serializer, user):
        new_parking_space = ParkingSpace.objects.create(
                cod = serializer.validated_data['cod'],
                status = serializer.validated_data['status'],
                parking = serializer.validated_data['parking'],
                created_by = user,
            )
        return new_parking_space
    
class TicketService:

    def create(self, serializer, user):
        new_ticket= Ticket.objects.create(
                model = serializer.validated_data['model'],
                license_plate = serializer.validated_data['license_plate'],
                checkin = serializer.validated_data['checkin'],
                checkout = serializer.validated_data['checkout'],
                parking_space = serializer.validated_data['parking_space'],
                value = serializer.validated_data['value'],
                created_by = user,
            )
        return new_ticket
    
    def calc_ticket(self, ticket):
        
        reference_date = datetime.now().date()

        combined_checkin = datetime.combine(reference_date, ticket.checkin)
        combined_checkout = datetime.combine(reference_date, ticket.checkout)
            
        total_time = combined_checkout - combined_checkin
        ticket.value = total_time.total_seconds() / 3600 *ticket.parking_space.parking.hour_price
        ticket.save()
        return ticket