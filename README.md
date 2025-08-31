# Movie Ticket Booking System

A production-ready Movie Ticket Booking System built with FastAPI.

## Features

### User Features
- User registration and authentication (JWT)
- Browse available movies
- View showtimes
- Book seats
- Cancel bookings
- View booking history

### Admin Features
- Add/update/delete movies
- Manage showtimes
- Admin authentication and authorization

## Tech Stack

- **Backend**: FastAPI
- **Database**: SQLite (can be easily switched to PostgreSQL)
- **Authentication**: JWT tokens
- **Password Hashing**: bcrypt
- **API Documentation**: Auto-generated Swagger UI and ReDoc

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd movie-ticket-booking

python -m scripts.create_admin
python3 -m http.server 3000
http://localhost:3000/