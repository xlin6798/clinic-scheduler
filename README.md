# 🏥 Clinic Scheduler

## 💡 Project Summary

Built a full-stack clinic scheduling system that simulates real-world healthcare workflows, including patient management, appointment scheduling, and facility-level configuration.

Designed and implemented both frontend and backend systems with a focus on usability, scalability, and clean data modeling. This project goes beyond basic CRUD by incorporating role-based access, dynamic configuration, and real-time UI interactions.

---

## 🌐 Live Demo

https://clinic-scheduler-seven.vercel.app/

---

## 🚀 Key Highlights

- 🔎 Real-time Patient Search
  - Debounced search with filtering by name, DOB, and MRN
  - Reduced unnecessary API calls and improved responsiveness

- 📅 Appointment Scheduling System
  - Day-based calendar view with drag-and-drop rescheduling
  - Full create/edit/delete workflow with validation

- 🧑‍⚕️ Patient Management System
  - Unified create/edit modal
  - MRN system-controlled and immutable
  - Integrated seamlessly with appointment flow

- 🏢 Facility-Based Configuration
  - Dynamic configuration for statuses, visit types, and genders
  - Eliminated hardcoded enums for scalability

- 🔐 Authentication & Access Control
  - JWT-based authentication
  - Facility-scoped data access

---

## 🧠 Technical Strengths

- Full-stack development (React + Django REST Framework)
- Relational database design with PostgreSQL
- Handling schema changes (CharField → ForeignKey)
- API design and validation
- UI state management for complex workflows
- Performance optimization (debouncing, pagination)
- Debugging migrations and database permissions

---

## ⚙️ Tech Stack

Frontend: React, Tailwind CSS, Material UI  
Backend: Django, Django REST Framework  
Database: PostgreSQL  
Deployment: Render

---

## 🧪 Local Setup

```bash
git clone https://github.com/your-username/clinic-scheduler.git
cd clinic-scheduler/backend

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "clinic_scheduler",
        "USER": "clinic_user",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5433",
    }
}
```

### Run
```bash
python manage.py migrate
python manage.py seed_demo --reset-appointments
python manage.py runserver
```

---

## 🔑 Demo Credentials

Username: admin  
Password: Admin123!

---

## 🧠 What I Learned

- Designing scalable relational data models
- Managing schema migrations and breaking changes
- Building intuitive UI tied to backend constraints
- Implementing authentication and multi-tenant logic
- Debugging database and deployment issues
