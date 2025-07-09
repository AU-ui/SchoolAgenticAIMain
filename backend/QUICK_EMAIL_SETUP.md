# Quick Email Setup Guide

## Why Email Service is Disabled

The backend shows "📧 Email service: ❌ Disabled" because email credentials are not configured.

## Quick Fix - Add to your .env file:

Add these lines to your `backend/.env` file:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
FRONTEND_URL=http://localhost:3000
```

## For Gmail Users:

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to Google Account → Security → App passwords
   - Select "Mail" and your device
   - Copy the generated password
3. **Use the app password** as `EMAIL_PASSWORD` (not your regular password)

## Example .env file:

```env
# Server Configuration
PORT=5000
NODE_ENV=development

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=edtech_platform
DB_USER=postgres
DB_PASSWORD=your_password

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=24h

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
FRONTEND_URL=http://localhost:3000
```

## Test Email Configuration:

After adding the email settings, restart your backend and test:

```bash
cd backend
node test-email.js
```

## Alternative: Use Test Email

If you don't want to set up real email right now, you can use a test email service like Mailtrap or just test the flow without actual email sending.

The registration flow will still work - users will be created but won't receive verification emails until you configure email. 