# WInki - Vehicle & Alloy Wheel Refurbishment Bookkeeping System

## Overview

WInki is a comprehensive Django-based bookkeeping application designed for vehicle and alloy wheel refurbishment businesses. It provides complete job tracking, customer management, payment processing, and business analytics.

## Features

- **Customer Management** - Complete customer profiles with contact details and job history
- **Job Tracking** - Multi-step job creation with vehicle/alloy wheel details and status management  
- **Payment System** - Deposit tracking, balance calculations, and payment history
- **QR Code System** - Job tracking via QR codes for mobile access
- **Reporting & Analytics** - Financial, operational, and customer reports
- **Black & White Theme** - Clean, minimalist interface using Tailwind CSS

## Technology Stack

- **Backend**: Django 5.2 LTS + PostgreSQL
- **Frontend**: Tailwind CSS (standalone mode) + Alpine.js
- **Development**: SQLite (local) → PostgreSQL (production)
- **Deployment**: Vercel ready

## Quick Start

1. **Clone and Setup**
```bash
cd winki
python -m venv winki_env
source winki_env/bin/activate  # On Windows: winki_env\Scripts\activate
pip install -r requirements.txt
```

2. **Database Setup**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py populate_sample_data
```

3. **Run Development Server**
```bash
python manage.py tailwind build  # Build Tailwind CSS
python manage.py runserver
```

4. **Access Application**
- Homepage: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Dashboard: http://127.0.0.1:8000/dashboard/

## Default Login

- **Username**: admin
- **Password**: admin123

## Project Structure

```
winki/
├── manage.py
├── requirements.txt
├── winki_project/          # Django settings
├── apps/                   # Application modules
│   ├── core/              # Dashboard and core functionality
│   ├── customers/         # Customer management
│   ├── jobs/              # Job tracking
│   ├── payments/          # Payment processing
│   └── reports/           # Analytics and reporting
├── templates/             # Django templates
├── theme/                 # Tailwind CSS theme
└── media/                 # User uploads
```

## Key Models

- **Customer** - Customer information and contact details
- **Job** - Main job tracking with auto-generated job IDs (WINKI-YYYY-NNNN)
- **VehicleDetails** - Vehicle-specific information
- **AlloyWheelDetails** - Wheel-specific information  
- **Payment** - Payment tracking with multiple payment types
- **Service** - Individual services within jobs

## Business Features

- Automatic job ID generation
- Outstanding balance calculations
- QR code generation for quick lookup
- Photo attachments (before/after)
- Payment reminders and notifications
- Comprehensive reporting system

## Development

- Built with Django 5.2 LTS for long-term stability
- Tailwind CSS v4 standalone for styling
- Responsive design for desktop and mobile
- Clean black & white minimalist theme
- Comprehensive admin interface

## Production Deployment

Ready for deployment on Vercel with:
- PostgreSQL database configuration
- Static file optimization
- Environment-based settings
- Production security headers

---

**WInki** - Professional refurbishment management made simple.