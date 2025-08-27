# 📧 Email Configuration Setup Guide

## 🎯 Overview
This guide will help you set up email functionality for the EdTech Platform using Gmail SMTP.

## 🚀 Quick Setup

### Step 1: Create .env file
Run the setup script:
```bash
cd backend
node setup-email-config.js
```

### Step 2: Gmail App Password Setup
1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and your device
   - Copy the generated 16-character password

### Step 3: Test Configuration
```bash
node test-email.js
```

## 📋 Manual Setup

If you prefer manual setup, create a `.env` file in the `backend` folder:

```env
# Email Configuration (for Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com

# Other required settings
FRONTEND_URL=http://localhost:3000
```

## 🔧 Configuration Details

### Gmail Settings
- **SMTP Host**: `smtp.gmail.com`
- **Port**: `587` (TLS) or `465` (SSL)
- **Security**: TLS/SSL enabled
- **Authentication**: Required

### Other Email Providers

#### Outlook/Hotmail
```env
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USER=your_email@outlook.com
EMAIL_PASSWORD=your_password
```

#### Yahoo
```env
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USER=your_email@yahoo.com
EMAIL_PASSWORD=your_app_password
```

## 🧪 Testing

### Test Email Configuration
```bash
node test-email.js
```

### Test via API
```bash
curl http://localhost:5000/api/landing/test-email
```

### Check Server Logs
When you start the backend server, you should see:
```
📧 Email service: ✅ Enabled
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Authentication Failed
**Error**: `Invalid login: 535-5.7.8 Username and Password not accepted`

**Solution**:
- Use App Password, not regular password
- Enable 2-Factor Authentication
- Generate new App Password

#### 2. Connection Timeout
**Error**: `Connection timeout`

**Solution**:
- Check internet connection
- Verify SMTP settings
- Try different port (465 instead of 587)

#### 3. Email Not Received
**Solution**:
- Check spam folder
- Verify email address
- Check Gmail sending limits

### Debug Mode
Add to your `.env` file:
```env
EMAIL_DEBUG=true
```

## 📧 Email Templates

The system includes these email templates:

1. **Verification Email**: 6-digit code for login/registration
2. **Welcome Email**: Sent after email verification
3. **Contact Form**: Admin notifications
4. **Test Email**: Configuration verification

## 🔒 Security Notes

- ✅ Never commit `.env` file to version control
- ✅ Use App Passwords instead of regular passwords
- ✅ Enable 2-Factor Authentication
- ✅ Monitor email sending limits
- ✅ Use environment-specific configurations

## 📊 Email Features

- **HTML Templates**: Professional design with branding
- **Plain Text Fallback**: For email clients that don't support HTML
- **Responsive Design**: Works on mobile and desktop
- **Error Handling**: Graceful fallbacks when email fails
- **Rate Limiting**: Prevents spam and abuse

## 🎉 Success Indicators

When email is properly configured:

1. ✅ Server starts with "📧 Email service: ✅ Enabled"
2. ✅ `node test-email.js` sends test email successfully
3. ✅ User registration sends verification emails
4. ✅ Contact form sends admin notifications
5. ✅ Email templates display correctly

## 📞 Support

If you encounter issues:

1. Check this troubleshooting guide
2. Verify Gmail App Password setup
3. Test with `node test-email.js`
4. Check server logs for error messages
5. Ensure `.env` file is in the correct location

---

**Note**: Email functionality is optional. The platform will work without email, but users won't receive verification emails or notifications.
