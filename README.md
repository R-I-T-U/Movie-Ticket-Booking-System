# 🎬 Movie Ticket Booking System

A **Movie Ticket Booking System** built with **FastAPI**. This system allows users to browse movies, book tickets, and provides an admin panel to manage listings.

---

## ✨ Features

- 🔑 User authentication & admin creation
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
2. ```bash
   git clone https://github.com/R-I-T-U/Movie-Ticket-Booking-System.git  
   cd Movie-Ticket-Booking-System
   ```
3. Create a virtual environment (recommended):

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

5. Install dependencies:
   ```bash
   pip install -r requirements/base.txt
   ```

6. Set up environment variables:  
   DATABASE_URL=your_database_url
   
9. Run database migrations:
    ```bash
    alembic upgrade head
    ```

11. Create an admin user:
    ```bash
    python -m scripts.create_admin
    ```
    
---

## ▶️ Steps to Run the Application

1. Start the FastAPI server:
   ```bash
   fastapi dev app/main.py
   ```

3. Access the backend:  
- API Base URL: http://localhost:8000  
- Swagger Documentation: http://localhost:8000/docs

3. Access the frontend:  
-http://localhost:5500/frontend/index.html

---

## Python Version and Libraries Used

### Python Version
- Python 3.8+

### Core Libraries
- FastAPI: Web framework
- SQLAlchemy: ORM for database operations
- python-dotenv: Environment variable management
- Werkzeug: Password hashing and security utilities

### Development Libraries
- pytest: Testing framework
- Faker: Test data generation
- HTTPX: HTTP client for testing

---

## 🚀 Deployment Instructions

### Deploy Locally with Uvicorn
1. Ensure all dependencies are installed:  
pip install -r requirements/base.txt

2. Run database migrations:  
alembic upgrade head

3. Start the FastAPI application:  
uvicorn app.main:app --host 0.0.0.0 --port 8000

4. Access the application:  
- API Base URL: http://127.0.0.1:8000  
- API Docs: http://127.0.0.1:8000/docs


---

## 🙌 Acknowledgments

Special thanks to all contributors and the open-source community for their support in building this project.
