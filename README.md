# 🎬 Movie Ticket Booking System

A production-ready **Movie Ticket Booking System** built with **FastAPI**. This system allows users to browse movies, book tickets, and provides an admin panel to manage listings.

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
   git clone https://github.com/R-I-T-U/Movie-Ticket-Booking-System.git  
   cd Movie-Ticket-Booking-System

2. Create a virtual environment (recommended):

   For Linux/Mac:  
   python -m venv venv  
   source venv/bin/activate  

   For Windows:  
   python -m venv venv  
   source venv\Scripts\activate  

3. Install dependencies:  
   pip install -r requirements/base.txt

4. Set up environment variables:  
   Create a `.env` file in the root directory and configure the required environment variables:
   DATABASE_URL=your_database_url SECRET_KEY=your_secret_key ACCESS_TOKEN_EXPIRE_MINUTES=30
5. Run database migrations:  
alembic upgrade head

6. Create an admin user:  
python -m scripts.create_admin

---

## ▶️ Steps to Run the Application

1. Start the FastAPI server:  
uvicorn app.main:app --reload

2. Access the backend:  
- API Base URL: http://localhost:8000  
- Swagger Documentation: http://localhost:8000/docs

3. Access the frontend (if applicable):  
http://localhost:5500/frontend/index.html

---

## 🐍 Python Version and Libraries Used

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

## 📄 License

This project is licensed under the MIT License.

---

## 🙌 Acknowledgments

Special thanks to all contributors and the open-source community for their support in building this project.