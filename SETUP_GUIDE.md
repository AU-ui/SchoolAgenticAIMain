# 🚀 EdTech Platform Setup Guide

## 📋 Prerequisites

- **Node.js** (v16 or higher)
- **PostgreSQL** (v13 or higher)
- **Git**

## 🗄️ Database Setup

### 1. Install PostgreSQL
- Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
- Create a database named `edtech_platform`

### 2. Configure Database
```sql
-- Connect to PostgreSQL and run:
CREATE DATABASE edtech_platform;
```

## 🔧 Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Environment Configuration
Copy the environment example file:
```bash
cp env.example .env
```

Edit `.env` with your configuration:
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=edtech_platform
DB_USER=postgres
DB_PASSWORD=your_actual_password

# JWT Configuration
JWT_SECRET=your_super_secret_jwt_key_here_make_it_long_and_random
JWT_EXPIRES_IN=24h
JWT_EMAIL_VERIFY_SECRET=your_email_verification_secret_key

# Server Configuration
PORT=5000
NODE_ENV=development
CORS_ORIGIN=http://localhost:3000

# Email Configuration (Optional - for email verification)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
EMAIL_FROM=your_email@gmail.com

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

### 4. Setup Database Schema
```bash
npm run db:setup
```

### 5. Test Database Connection
```bash
npm run db:test
```

### 6. Start Backend Server
```bash
npm run dev
```

The backend will be running on `http://localhost:5000`

## 🎨 Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend/app
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Environment Configuration (Optional)
Copy the environment example file:
```bash
cp env.example .env
```

Edit `.env`:
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENV=development
```

### 4. Start Frontend Development Server
```bash
npm start
```

The frontend will be running on `http://localhost:3000`

## 🔐 Default Login Credentials

The system comes with a default superadmin account:

- **Email**: `superadmin@edtech.com`
- **Password**: `admin123`

## 🧪 Testing the Setup

### 1. Test Backend Health
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "success": true,
  "message": "EdTech Platform Backend is running",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "environment": "development"
}
```

### 2. Test Frontend
- Open `http://localhost:3000` in your browser
- You should see the landing page
- Try logging in with the default credentials

### 3. Test API Endpoints
```bash
# Test login endpoint
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@edtech.com","password":"admin123"}'
```

## 🐛 Troubleshooting

### Backend Issues

1. **Database Connection Failed**
   - Check PostgreSQL is running
   - Verify database credentials in `.env`
   - Ensure database `edtech_platform` exists

2. **Port Already in Use**
   - Change `PORT` in `.env` file
   - Or kill the process using port 5000

3. **JWT Secret Missing**
   - Ensure `JWT_SECRET` is set in `.env`
   - Generate a strong random string

### Frontend Issues

1. **API Connection Failed**
   - Ensure backend is running on port 5000
   - Check `REACT_APP_API_URL` in `.env`
   - Verify CORS settings in backend

2. **Build Errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

## 📁 Project Structure

```
edtech-platform/
├── backend/
│   ├── src/
│   │   ├── routes/api/          # API endpoints
│   │   ├── middleware/          # Auth & validation
│   │   ├── config/             # Database & config
│   │   └── services/           # Business logic
│   ├── database/               # Database schema & setup
│   └── .env                    # Environment variables
├── frontend/app/
│   ├── src/
│   │   ├── pages/              # React components
│   │   ├── components/         # Reusable components
│   │   └── config/             # API configuration
│   └── .env                    # Frontend environment
└── mlservices/                 # ML microservices (to be implemented)
```

## 🚀 Next Steps

1. **Email Setup**: Configure email service for verification emails
2. **ML Services**: Implement Python ML microservices
3. **Production**: Set up production environment variables
4. **Testing**: Add comprehensive test suites
5. **Deployment**: Deploy to cloud platforms

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure environment variables are correctly set
4. Check console logs for detailed error messages 