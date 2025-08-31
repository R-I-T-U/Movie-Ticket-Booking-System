# 🎬 Movie Ticket Booking System

A **Movie Ticket Booking System** built with **FastAPI**. This system allows users to browse movies, book tickets, and provides an admin panel to manage movies and showtimes.

---

## ✨ Features

- 🔑 User authentication
- 🎥 Manage movies & showtimes
- 🎟 Ticket booking system
- ⚡ FastAPI backend with auto-generated API documentation (`/docs`)

---

## 📌 Prerequisites

Ensure you have the following installed before setting up:

- **Python**: `>=3.8`
- **pip**: Python package manager
- **Git**: Version control system

---

## ⚙️ Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/R-I-T-U/Movie-Ticket-Booking-System.git  
   cd Movie-Ticket-Booking-System
   ```
2. Create a virtual environment (recommended):

   For Linux/Mac:
   ```bash
   python -m venv venv  
   source venv/bin/activate
   ```
   
   For Windows:
   ```bash
   python -m venv venv  
   source venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements/base.txt
   ```

4. Set up environment variables:  
   echo "DATABASE_URL=postgresql://your_username:your_password@localhost:5432/movie_booking" > .env
- Replace your_username and your_password with your actual data
   
6. Run database migrations:
    ```bash
    alembic upgrade head
    ```

7. Create an admin user:
    ```bash
    python -m scripts.create_admin
    ```
    
---

## ▶️ Steps to Run the Application

1. Start the FastAPI server:
- Make sure you are in the Movie-Ticket-Booking-System directory in your terminal.
- Make sure your virtual environment is activated (if you have one set up).
   ```bash
   fastapi dev app/main.py
   ```

3. Access the backend:  
- API Base URL: http://localhost:8000  
- Swagger Documentation: http://localhost:8000/docs

3. Access the frontend:  
- Option 1: Simply run the HTML file by Live Server or open the file directly in your browser.
- Option 2: Run an HTTP server on port 3000 using this command:
  ```bash
  python -m http.server 3000
  ```
  Then open your browser and visit:
  http://localhost:3000 
