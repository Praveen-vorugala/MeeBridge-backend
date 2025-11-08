# MeeBridge - Meeting Booking Platform

A comprehensive meeting booking platform that allows businesses to create customized booking pages, manage availability, and track analytics.

## Project Structure

```
MeeBridge/
├── meebridge_backend/        # Django REST API Backend
│   ├── users/                # User authentication & management
│   ├── meeting_pages/        # Meeting page builder & customization
│   ├── bookings/             # Booking management & availability
│   └── analytics/            # Analytics & KPI tracking
└── meebridge-frontend/       # Angular 15 Frontend
    ├── src/app/
    │   ├── auth/             # Authentication module
    │   ├── dashboard/        # Dashboard with KPIs & charts
    │   ├── builder/          # Page builder for fields & styling
    │   ├── calendar/         # Availability management
    │   ├── booking/          # Public booking page
    │   └── admin/            # Admin portal
```

## Backend Setup (Django)

1. Navigate to the backend directory:
```bash
cd MeeBridge
source venv/bin/activate
```

2. Install dependencies (already installed):
```bash
pip install django djangorestframework django-cors-headers python-decouple Pillow
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

5. Start the Django server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api`

## Frontend Setup (Angular 15)

1. Navigate to the frontend directory:
```bash
cd meebridge-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:4200`

## Default Login Credentials

- Email: `admin@meebridge.com`
- Password: `admin123`

## Features

### ✅ Completed

1. **Backend (Django REST API)**
   - User authentication with custom User model
   - Meeting page CRUD operations
   - Booking management
   - Availability management
   - Analytics endpoints
   - Public booking endpoints

2. **Frontend (Angular 15)**
   - Authentication module with login
   - Dashboard with KPIs and charts
   - Page builder module (basic structure)
   - Material UI integration
   - Routing with lazy loading
   - Layout component with navigation

### 🚧 In Progress / To Be Enhanced

1. **Page Builder**
   - Drag-and-drop field reordering
   - Field type customization
   - Theme customization UI
   - Logo/image upload
   - Live preview

2. **Calendar/Availability**
   - Availability schedule UI
   - Time slot management
   - Recurring availability

3. **Public Booking Page**
   - Dynamic form rendering
   - Time slot selection
   - Booking confirmation
   - Email notifications

4. **Admin Portal**
   - User management
   - System analytics
   - Platform settings

## API Endpoints

### Authentication
- `POST /api/users/login/` - Login
- `POST /api/users/register/` - Register
- `GET /api/users/me/` - Get current user

### Meeting Pages
- `GET /api/meeting-pages/` - List meeting pages
- `POST /api/meeting-pages/` - Create meeting page
- `GET /api/meeting-pages/{id}/` - Get meeting page
- `PATCH /api/meeting-pages/{id}/` - Update meeting page
- `DELETE /api/meeting-pages/{id}/` - Delete meeting page
- `GET /api/public/meeting-pages/{slug}/` - Get public meeting page

### Bookings
- `GET /api/bookings/` - List bookings
- `POST /api/public/bookings/` - Create booking (public)
- `GET /api/bookings/upcoming/` - Get upcoming bookings
- `POST /api/bookings/{id}/cancel/` - Cancel booking
- `GET /api/public/bookings/available-slots/` - Get available slots

### Availability
- `GET /api/availabilities/` - List availabilities
- `POST /api/availabilities/` - Create availability
- `PATCH /api/availabilities/{id}/` - Update availability
- `DELETE /api/availabilities/{id}/` - Delete availability

### Analytics
- `GET /api/analytics/` - Get analytics data

## Development Notes

- Backend uses SQLite by default (can be changed to MySQL in settings.py)
- CORS is configured for localhost:4200
- Session authentication is used (can be extended with JWT)
- Media files are served from `/media/` in development

## Next Steps

1. Complete the page builder UI with drag-and-drop
2. Implement calendar/availability management UI
3. Create public booking page with dynamic forms
4. Add email notification system
5. Implement file upload for logos/images
6. Add more chart types and analytics
7. Create admin portal for platform management

