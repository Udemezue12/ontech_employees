# Ontech Employees – Task Management System

A modern and secure employee task management system built with **Django REST Framework (DRF)** and **React**, featuring **biometric authentication (WebAuthn)** for secure login and logout. The platform streamlines task assignment, attendance tracking, and employee management in real time.

---

## 🚀 Features

### 🔐 Biometric Authentication (WebAuthn)
- Passwordless login using Fingerprint / Face ID
- FIDO2-compliant authentication using platform authenticators (Windows Hello, Android Biometrics, Touch ID, etc.)
- Biometric logout/sign-out confirmation

### 👥 User Management
- Role-based access (Admin, Manager, Employee)
- Secure user registration and onboarding
- WebAuthn key registration per user

### 📋 Task Management
- Create, assign, and track tasks
- Task filtering by status, priority, or assignee
- Mark tasks as completed or in progress

### ⏱️ Attendance & Activity Tracking
- Employee sign-in/sign-out logs (biometric-secured)
- Task duration and activity monitoring
- Optional location-aware clock-ins

### 💻 Tech Stack
- **Backend**: Django + Django REST Framework (DRF)
- **Frontend**: React (with hooks and context API)
- **Authentication**: WebAuthn + Django session/JWT
- **Database**: PostgreSQL (or your preferred DB)
- **Optional**: Celery + Redis for background tasks

---

## 📦 Installation

### Backend (Django)

```bash
git clone https://github.com/Udemezue12/ontech_employees.git
cd ontech_employees/backend
python -m venv env
source env/bin/activate  # or .\env\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
Frontend (React)
bash
Copy
Edit
cd ../frontend
npm install
npm start
📸 Screenshots (Optional)
Include screenshots/gifs of:

Biometric Login

Task Assignment UI

Dashboard View

Sign Out prompt using biometrics

📚 API Endpoints (Sample)
Method	Endpoint	Description
POST	/api/auth/register/	Register new user
POST	/api/auth/webauthn/begin-login/	Start biometric login
POST	/api/auth/webauthn/verify-login/	Complete biometric login
POST	/api/tasks/	Create new task
GET	/api/tasks/	List all tasks
PATCH	/api/tasks/<id>/	Update task status
POST	/api/auth/signout/	Biometric-protected logout

🔒 Security Notes
FIDO2 and WebAuthn ensure public/private key-based authentication.

No sensitive credential or password is stored on the server.

CSRF protection and secure cookie/session handling enabled in Django.

🧪 Testing
Backend: pytest or unittest

Frontend: jest, react-testing-library

WebAuthn test tools available in Chrome DevTools or virtual authenticators



📄 License
This project is licensed under the Astrotech License.

🙌 Acknowledgments
WebAuthn.io
Django REST Framework
React