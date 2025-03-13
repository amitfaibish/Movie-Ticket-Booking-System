from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bson import ObjectId
import pymongo

app = FastAPI()

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["movie_booking_system"]

# Models
class TicketBooking(BaseModel):
    userId: str
    movie_title: str
    showtime_id: str
    seat_number: int
    price: float
    theater: str


class TicketUpdate(BaseModel):
    userId: str
    showtime_id: str
    seat_number: int
    new_seat_number: int = None
    action: str  # "cancel" or "change"


# 1. Allow customers to book tickets
@app.post("/book_ticket/")
async def book_ticket(ticket: TicketBooking):
    # Retrieve movie and showtime documents
    movie = db.movies.find_one({"title": ticket.movie_title})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Convert showtime_id from string to ObjectId
    try:
        showtime_id = ObjectId(ticket.showtime_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid showtime_id format")
    
    showtime = db.showtimes.find_one({"_id": showtime_id})
    if not showtime:
        raise HTTPException(status_code=404, detail="Showtime not found")

    # 2. Ensure no seat is booked twice for the same showtime
    if any(booking['seat_number'] == ticket.seat_number for booking in showtime['bookings']):
        raise HTTPException(status_code=400, detail="Seat is already booked")

    # 3. Check if the maximum number of seats has been reached
    max_seats = showtime.get('max_seats', 100)  # Default 100 if not specified
    if len(showtime['bookings']) >= max_seats:
        raise HTTPException(status_code=400, detail="Maximum number of seats reached")

    # Create the booking
    booking = {
        "userId": ticket.userId,
        "seat_number": ticket.seat_number,
        "price": ticket.price,
        "movie_title": ticket.movie_title,
        "theater": ticket.theater
    }

    # Add the booking to the showtime's bookings array
    db.showtimes.update_one({"_id": showtime_id}, {"$push": {"bookings": booking}})
    
    return {"message": "Ticket booked successfully"}


# 4. Allow customers to cancel or change tickets up to 3 hours before the showtime
@app.post("/update_ticket/")
async def update_ticket(ticket_update: TicketUpdate):
    try:
        showtime_id = ObjectId(ticket_update.showtime_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid showtime_id format")

    showtime = db.showtimes.find_one({"_id": showtime_id})
    if not showtime:
        raise HTTPException(status_code=404, detail="Showtime not found")

    # Find the booking to update or cancel
    booking = next((booking for booking in showtime['bookings'] if booking['userId'] == ticket_update.userId and booking['seat_number'] == ticket_update.seat_number), None)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # 5. Check if we are within 3 hours of the showtime
    showtime_time = datetime.strptime(showtime["time"], "%Y-%m-%dT%H:%M:%S")
    if datetime.now() > showtime_time - timedelta(hours=3):
        raise HTTPException(status_code=400, detail="Cannot cancel or change ticket less than 3 hours before the showtime")

    # 6. Perform the action (cancel or change)
    if ticket_update.action == "cancel":
        db.showtimes.update_one({"_id": showtime_id}, {"$pull": {"bookings": {"userId": ticket_update.userId, "seat_number": ticket_update.seat_number}}})
        return {"message": "Ticket canceled successfully"}
    
    elif ticket_update.action == "change" and ticket_update.new_seat_number is not None:
        # Check if the new seat number is already booked
        if any(booking['seat_number'] == ticket_update.new_seat_number for booking in showtime['bookings']):
            raise HTTPException(status_code=400, detail="New seat is already booked")

        # Update the seat number
        db.showtimes.update_one(
            {"_id": showtime_id, "bookings.userId": ticket_update.userId, "bookings.seat_number": ticket_update.seat_number},
            {"$set": {"bookings.$.seat_number": ticket_update.new_seat_number}}
        )
        return {"message": "Ticket updated successfully"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")


# 7. Track booking details
@app.get("/bookings/{userId}")
async def get_user_bookings(userId: str):
    bookings = db.showtimes.find({"bookings.userId": userId})
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for this user")
    
    result = []
    for showtime in bookings:
        for booking in showtime['bookings']:
            if booking['userId'] == userId:
                result.append({
                    "showtime_id": str(showtime["_id"]),
                    "movie_title": showtime["movie_title"],
                    "theater": showtime["theater"],
                    "seat_number": booking['seat_number'],
                    "price": booking['price'],
                })

    return result
