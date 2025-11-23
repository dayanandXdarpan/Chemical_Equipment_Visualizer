# Chemical Equipment Parameter Visualizer

## 🧪 Hybrid Web + Desktop Application

A full-stack application for visualizing and analyzing chemical equipment parameters with both Web and Desktop interfaces, featuring user authentication, data management, and deployment-ready configurations.

## 📋 Project Overview

This hybrid application allows users to:
- Register and authenticate securely
- Upload CSV files containing chemical equipment data
- View and edit data in interactive tables
- Visualize data with charts (Chart.js for web, Matplotlib for desktop)
- Generate PDF reports
- Store history of uploaded datasets
- Manage user profiles and password recovery
- Deploy to production (Vercel for frontend, Render for backend)

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend (Web)** | React.js + Chart.js | Interactive web interface with charts and authentication |
| **Frontend (Desktop)** | PyQt5 + Matplotlib | Desktop application with native UI |
| **Backend** | Django + Django REST Framework | RESTful API backend with authentication |
| **Data Processing** | Pandas | CSV parsing and analytics |
| **Database** | SQLite / MongoDB | Store datasets and user data |
| **Authentication** | JWT/Token-based | Secure user authentication with password reset |
| **Deployment** | Vercel + Render | Production hosting |

## 📁 Project Structure

```
fossee/
├── .git/                      # Git repository
├── .gitignore                 # Git ignore rules
├── backend/                   # Django Backend
│   ├── .env.production        # Production environment variables
│   ├── .gitignore             # Backend-specific ignores
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── settings.py        # Django settings (SQLite)
│   │   ├── settings_mongodb.py # MongoDB settings
│   │   ├── urls.py            # URL routing
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── equipment/             # Main app
│   │   ├── __init__.py
│   │   ├── admin.py           # Admin configuration
│   │   ├── apps.py
│   │   ├── auth_views.py      # Authentication views
│   │   ├── dynamic_csv_handler.py # CSV processing
│   │   ├── migrations/        # Database migrations
│   │   ├── models.py          # Database models
│   │   ├── serializers.py     # DRF serializers
│   │   ├── urls.py            # App URLs
│   │   └── views.py           # API views
│   ├── manage.py
│   ├── media/                 # Uploaded files storage
│   ├── render.yaml            # Render deployment config
│   ├── requirements.txt
│   ├── db.sqlite3             # SQLite database
│   └── venv/                  # Virtual environment
├── frontend/                  # React Frontend
│   ├── .env.development       # Development environment
│   ├── .env.production        # Production environment
│   ├── .gitignore
│   ├── build/                 # Production build
│   ├── node_modules/          # Dependencies
│   ├── package.json
│   ├── package-lock.json
│   ├── public/
│   │   ├── index.html
│   │   └── logo.png
│   ├── src/
│   │   ├── api.js             # API configuration
│   │   ├── App.css
│   │   ├── App.js             # Main component
│   │   ├── components/
│   │   │   ├── Auth.css
│   │   │   ├── Auth.js        # Login/Register
│   │   │   ├── CSVDataEditor.css
│   │   │   ├── CSVDataEditor.js # Data editing interface
│   │   │   ├── DatasetList.css
│   │   │   ├── DatasetList.js # Dataset history
│   │   │   ├── DataVisualization.css
│   │   │   ├── DataVisualization.js # Charts & tables
│   │   │   ├── FileUpload.css
│   │   │   ├── FileUpload.js  # CSV upload
│   │   │   ├── ForgotPassword.css
│   │   │   ├── ForgotPassword.js # Password reset
│   │   │   ├── UserProfile.css
│   │   │   └── UserProfile.js # User profile management
│   │   ├── index.css
│   │   └── index.js
│   └── vercel.json            # Vercel deployment config
├── desktop/                   # PyQt5 Desktop App
│   ├── main.py                # Desktop application
│   ├── requirements.txt
│   └── venv/                  # Virtual environment
└── test_data/                 # Test data
    └── sample_equipment_data.csv
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+ installed
- Node.js 14+ and npm installed
- Git installed

### 1. Clone the Repository

```powershell
cd c:\Users\deepa\Desktop\fossee
```

### 2. Backend Setup (Django)

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Backend will be available at: `http://localhost:8000`

### 3. Frontend Setup (React)

Open a **new PowerShell window**:

```powershell
# Navigate to frontend directory
cd c:\Users\deepa\Desktop\fossee\frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will automatically open at: `http://localhost:3000`

### 4. Desktop App Setup (PyQt5)

Open a **new PowerShell window**:

```powershell
# Navigate to desktop directory
cd c:\Users\deepa\Desktop\fossee\desktop

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Run desktop application
python main.py
```

## 📊 Sample Data

A sample CSV file (`test_data/sample_equipment_data.csv`) is provided with the following structure:

| Equipment Name | Type | Flowrate | Pressure | Temperature |
|----------------|------|----------|----------|-------------|
| Heat Exchanger-001 | Heat Exchanger | 150.5 | 25.3 | 180.2 |
| Reactor-001 | Reactor | 200.0 | 50.0 | 250.5 |
| ... | ... | ... | ... | ... |

## 🔑 Key Features

### 1. User Authentication
- User registration and login
- Password reset via OTP
- JWT token-based authentication
- User profile management
- Account deletion

### 2. CSV Upload & Management
- Upload CSV files with equipment data
- Validates column structure
- Automatically parses and stores data
- Dataset history management

### 3. Data Editing
- Interactive table for data editing
- Real-time validation
- Save changes to database

### 4. Data Summary & Analytics
- Returns total equipment count
- Calculates average flowrate, pressure, temperature
- Provides equipment type distribution
- Advanced statistics and filtering

### 5. Visualizations
- **Web**: Interactive charts using Chart.js
  - Bar chart for average values
  - Pie chart for type distribution
  - Line charts for trends
- **Desktop**: Static charts using Matplotlib
  - Same visualizations in native desktop UI

### 6. PDF Report Generation
- **Web**: Uses jsPDF to generate reports
- **Desktop**: Uses ReportLab for PDF creation
- Includes summary statistics and data tables

### 7. Production Deployment
- **Frontend**: Deployed to Vercel
- **Backend**: Deployed to Render
- Environment-based configuration
- CORS and security settings

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user
- `POST /api/auth/forgot-password/` - Request password reset OTP
- `POST /api/auth/reset-password/` - Reset password with OTP
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `POST /api/auth/change-password/` - Change password
- `DELETE /api/auth/delete-account/` - Delete user account

### Datasets
- `GET /api/datasets/` - List user datasets
- `GET /api/datasets/{id}/` - Get dataset details
- `POST /api/datasets/upload/` - Upload CSV file
- `GET /api/datasets/{id}/summary/` - Get dataset summary
- `GET /api/datasets/{id}/advanced-stats/` - Get advanced statistics
- `POST /api/datasets/{id}/filter/` - Filter dataset
- `POST /api/datasets/{id}/export/` - Export dataset
- `DELETE /api/datasets/{id}/` - Delete dataset

## 🎯 Usage Guide

### Web Application

1. **Register/Login**
   - Open http://localhost:3000
   - Register a new account or login

2. **Upload CSV**
   - Click "Select File" and choose your CSV
   - Click "Upload" to process the file

3. **View & Edit Data**
   - Select a dataset from the history
   - View summary, data table, and charts
   - Edit data in the table and save changes

4. **User Management**
   - Access profile from the menu
   - Change password or update profile
   - Use forgot password if needed

5. **Export Report**
   - Click "Download PDF Report" to generate a report

### Desktop Application

1. **Login**
   - Run the desktop app
   - Login with your credentials

2. **Upload CSV**
   - Click "Select File"
   - Choose CSV and click "Upload"

3. **View Data**
   - Click on a dataset in the history
   - Switch between Summary, Data Table, and Charts tabs

4. **Export PDF**
   - Click "Export PDF Report"
   - Choose save location

## 🧪 Testing

### Test with Sample Data

1. Start all services (backend, frontend, desktop)
2. Register a new user
3. Upload `test_data/sample_equipment_data.csv`
4. Verify data appears correctly in:
   - Summary statistics
   - Data table
   - Charts
5. Edit some data and save
6. Generate and download PDF report
7. Test user profile features

## 🔧 Configuration

### Backend Configuration

Edit `backend/backend/settings.py`:

```python
# Debug mode (set to False in production)
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = ['*']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
```

For MongoDB, use `settings_mongodb.py`

### Frontend Configuration

Environment variables in `.env.development` and `.env.production`:

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_VERSION=1.0.0
```

### Deployment

- **Vercel**: Frontend deploys automatically from `main` branch
- **Render**: Backend deploys from `render.yaml` configuration

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```powershell
# Change port
python manage.py runserver 8001
```

**Database errors:**
```powershell
# Delete db.sqlite3 and recreate
del db.sqlite3
python manage.py migrate
```

### Frontend Issues

**Port 3000 in use:**
```powershell
# Set different port
$env:PORT=3001; npm start
```

**API connection errors:**
- Ensure backend is running
- Check REACT_APP_API_URL in .env files

### Desktop App Issues

**PyQt5 installation fails:**
```powershell
# Try installing with specific version
pip install PyQt5==5.15.9
```

**Connection refused:**
- Ensure Django backend is running
- Check API_BASE_URL in main.py

## 📝 Development Notes

### Adding New Features

1. **Backend**: Add new views in `equipment/views.py`
2. **Frontend**: Create new components in `src/components/`
3. **Desktop**: Modify `main.py` to add new windows/dialogs

### Database Models

- `User`: Custom user model with email uniqueness
- `Dataset`: Stores metadata about uploaded CSV files
- `Equipment`: Stores individual equipment records
- `PasswordResetOTP`: For password reset functionality

### API Authentication

Uses JWT tokens:
```javascript
headers = {
    'Authorization': `Bearer ${token}`
}
```

## 🎓 Learning Outcomes

This project demonstrates:
- Full-stack development with Django + React
- RESTful API design with authentication
- Desktop application development with PyQt5
- Data visualization (Chart.js, Matplotlib)
- PDF generation (jsPDF, ReportLab)
- JWT authentication and user management
- File upload and processing
- Database operations with Django ORM
- Production deployment (Vercel + Render)
- Environment-based configuration

## 📄 License

This project is created for educational purposes as part of the FOSSEE screening task.

## 👥 Author

Deepa - FOSSEE Screening Task 2025

## 🙏 Acknowledgments

- Django and Django REST Framework documentation
- React.js documentation
- PyQt5 documentation
- Chart.js and Matplotlib communities
- Vercel and Render deployment platforms

---

## Quick Start Summary

```powershell
# Terminal 1 - Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Terminal 2 - Frontend
cd frontend
npm install
npm start

# Terminal 3 - Desktop (optional)
cd desktop
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
python main.py
```

Access:
- Web App: http://localhost:3000
- API: http://localhost:8000/api
- Admin: http://localhost:8000/admin
- Desktop: Run main.py

**Happy Coding! 🚀**
