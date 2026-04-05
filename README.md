# Clinic Scheduler

A full-stack clinic appointment management system built with Django and React.

## Features

- Create appointments
- View appointments by facility
- Delete appointments
- Staff-based access control
- Authentication with Django sessions and CSRF protection

## Tech Stack

### Backend
- Django
- Django REST Framework

### Frontend
- React
- Vite
- Axios
- Bootstrap

## Security

- Session-based authentication
- CSRF protection
- Facility-level data isolation

## Project Structure

```text
clinic-scheduler/
├── backend/     # Django backend
└── frontend/    # React frontend
```

## Setup Instructions

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Log in at `http://localhost:8000/admin`
2. Open the frontend at `http://localhost:5173`

## Notes

- Uses a Vite proxy for local development
- Axios is configured to work with Django CSRF protection

## Author

Kevin Lin

## License

MIT
