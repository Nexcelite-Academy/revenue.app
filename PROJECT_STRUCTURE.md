# Tutoring Center Management System - Project Structure

## Overview
A comprehensive tutoring center management system with frontend interface and backend API for managing students, teachers, courses, payments, sessions, and financial reporting.

## Current Architecture

### Frontend (Client-Side)
```
edu-management/
├── index.html          # Main SPA entry point with Bootstrap navigation
├── app.js             # Core application logic and data store
├── style.css          # Custom design system with dark/light theme support
└── assets/            # Static assets (future)
```

### Frontend Technology Stack
- **HTML5** - Semantic markup structure
- **CSS3** - Custom design system with CSS variables
- **Vanilla JavaScript** - ES6+ application logic
- **Bootstrap 5.3.3** - UI components and responsive grid
- **Chart.js 4.4.0** - Dashboard visualization

### Current Data Model (In-Memory)
```javascript
store = {
  students: [
    {
      id: number,
      name: string,
      gender: 'M'|'F',
      birthdate: string,
      age: number,
      parent: string,
      contact: string,
      balances: { [courseName]: hours }
    }
  ],
  teachers: [
    {
      id: number,
      name: string,
      hourlyRate: number
    }
  ],
  courses: [
    {
      id: number,
      name: string,
      hourlyRate: number,
      teacherId: number
    }
  ],
  payments: [
    {
      date: string,
      studentId: number,
      courseId: number,
      teacherId: number,
      hourlyRate: number,
      purchasedHours: number,
      discountedTuition: number,
      amountPaid: number,
      paymentMethod: string
    }
  ],
  sessions: [
    {
      date: string,
      studentId: number,
      courseId: number,
      teacherId: number,
      startTime: string,
      endTime: string,
      hours: number
    }
  ],
  expenses: [
    {
      date: string,
      item: string,
      amount: number
    }
  ]
}
```

## Planned Architecture (Target)

### Backend (Server-Side)
```
backend/
├── app.py                 # Flask application entry point
├── config/
│   ├── database.py        # Database configuration
│   └── settings.py        # Application settings
├── models/
│   ├── student.py         # Student data model
│   ├── teacher.py         # Teacher data model
│   ├── course.py          # Course data model
│   ├── payment.py         # Payment data model
│   ├── session.py         # Session data model
│   └── expense.py         # Expense data model
├── api/
│   ├── routes/
│   │   ├── students.py    # Student CRUD endpoints
│   │   ├── teachers.py    # Teacher CRUD endpoints
│   │   ├── courses.py     # Course CRUD endpoints
│   │   ├── payments.py    # Payment endpoints
│   │   ├── sessions.py    # Session endpoints
│   │   └── reports.py     # Report generation endpoints
│   └── middleware/
│       ├── auth.py        # Authentication middleware
│       └── validation.py  # Request validation
├── services/
│   ├── calculations.py    # Business logic calculations
│   ├── reports.py         # Report generation service
│   └── notifications.py  # Email/SMS notifications
├── utils/
│   ├── validators.py      # Data validation utilities
│   └── helpers.py         # Helper functions
├── tests/
│   ├── test_models.py     # Model tests
│   ├── test_api.py        # API endpoint tests
│   └── test_services.py   # Service layer tests
├── migrations/            # Database migration files
├── requirements.txt       # Python dependencies
└── README.md             # Backend setup instructions
```

### Database Schema (SQLite/PostgreSQL)
- **students** table with balances relationship
- **teachers** table
- **courses** table with teacher FK
- **payments** table with student/course/teacher FKs
- **sessions** table with student/course/teacher FKs
- **expenses** table
- **users** table for authentication (future)

### Technology Stack (Target)
- **Backend**: Python Flask/FastAPI
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy
- **API**: RESTful JSON API
- **Authentication**: JWT tokens (future)
- **Testing**: pytest
- **Deployment**: Docker containers

## Core Features

### Current Features
1. **Student Management** - Add, edit, delete students with balance tracking
2. **Teacher Management** - Teacher profiles with hourly rates
3. **Course Management** - Course setup with teacher assignments
4. **Payment Processing** - Record payments and update student balances
5. **Session Logging** - Track teaching sessions and deduct balances
6. **Expense Tracking** - Record business expenses
7. **Financial Dashboard** - Revenue, costs, profit visualization
8. **Attendance Reports** - Teacher hours and salary calculations
9. **Financial Reports** - Comprehensive reporting with CSV export

### Planned Enhancements
1. **Data Persistence** - Database storage and retrieval
2. **Advanced Calculations** - Automated balance management
3. **Validation System** - Comprehensive data validation
4. **Error Handling** - Proper error responses and user feedback
5. **Performance Optimization** - Efficient data loading and caching
6. **Advanced Reporting** - More detailed analytics and insights

## Development Workflow

### Current Status
- ✅ Frontend UI/UX complete
- ✅ Basic functionality working
- ❌ No data persistence
- ❌ No backend API
- ❌ No advanced validation
- ❌ No error handling

### Next Milestones
1. **Backend Setup** - Flask app with database models
2. **API Development** - RESTful endpoints for all entities
3. **Frontend Integration** - Connect frontend to backend API
4. **Data Migration** - Move from in-memory to database storage
5. **Advanced Features** - Enhanced calculations and reporting
6. **Testing & Deployment** - Complete testing suite and deployment setup 