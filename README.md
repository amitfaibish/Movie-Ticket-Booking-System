# Movie-Ticket-Booking-System
for AT&amp;T

# Ticket Booking System - Backend

This is a backend system for a movie ticket booking platform built using FastAPI and connected to a MongoDB database. It allows customers to book, cancel, and change tickets for available showtimes, with various features to manage bookings and ensure no seat is double-booked.

## Features

### 1. **Book Tickets**
   - Allows customers to book tickets for available showtimes.
   - Ensures no seat is booked twice for the same showtime.
   - Tracks booking details, including `userId`, `movie`, `showtime`, `seat_number`, and `price`.
   - Configurable maximum number of seats per showtime.

### 2. **Cancel/Change Tickets**
   - Allows customers to cancel or change tickets up to 3 hours before the showtime starts.
   - If less than 3 hours remain, ticket cancellation or change is not allowed.

### 3. **Track Bookings**
   - Tracks user bookings, including showtime, seat number, movie title, and price.

### 4. **Prevent Double Booking**
   - Ensures no seat is booked more than once for the same showtime.

### 5. **Configurable Maximum Seats**
   - The maximum number of seats per showtime is configurable.

## Requirements

- Python 3.7+
- FastAPI
- pymongo (MongoDB driver for Python)
- MongoDB

## Installation

1. Install the required dependencies:
   ```bash
   pip install fastapi pymongo
