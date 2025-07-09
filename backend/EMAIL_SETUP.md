# Email Setup Guide

This guide will help you configure email functionality using Nodemailer for the EdTech Platform.

## Environment Variables

Add these variables to your `.env` file:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
FRONTEND_URL=http://localhost:3000
```

## Gmail Setup (Recommended)

### 1. Enable 2-Factor Authentication
- Go to your Google Account settings
- Enable 2-Factor Authentication

### 2. Generate App Password
- Go to Google Account → Security → App passwords
- Select "Mail" and your device
- Generate the app password
- Use this password as `EMAIL_PASSWORD` in your `.env` file

### 3. Alternative: Less Secure Apps (Not Recommended)
- Go to Google Account → Security → Less secure app access
- Turn on "Allow less secure apps"
- Use your regular Gmail password

## Other Email Providers

### Outlook/Hotmail
```env
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USER=your-email@outlook.com
EMAIL_PASSWORD=your-password
```

### Yahoo
```env
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USER=your-email@yahoo.com
EMAIL_PASSWORD=your-app-password
```

### Custom SMTP Server
```env
EMAIL_HOST=your-smtp-server.com
EMAIL_PORT=587
EMAIL_USER=your-username
EMAIL_PASSWORD=your-password
```

## Testing Email Configuration

Run this command to test your email setup:

```bash
node test-email.js
```

## Email Templates

The system includes two email templates:

1. **Verification Email**: Sent when users sign up
2. **Welcome Email**: Sent after email verification

Both emails include:
- Professional HTML design
- Plain text fallback
- Responsive layout
- Branded styling

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check your email and password
   - Ensure 2FA is enabled and app password is used (for Gmail)
   - Verify less secure apps is enabled (if using regular password)

2. **Connection Timeout**
   - Check your internet connection
   - Verify SMTP host and port
   - Check firewall settings

3. **Email Not Received**
   - Check spam folder
   - Verify email address is correct
   - Check email provider's sending limits

### Debug Mode

To enable debug logging, add this to your `.env`:

```env
EMAIL_DEBUG=true
```

## Security Notes

- Never commit your `.env` file to version control
- Use app passwords instead of regular passwords when possible
- Consider using environment-specific email configurations
- Monitor email sending limits and quotas 