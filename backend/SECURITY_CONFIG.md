# Security Configuration Guide

This document outlines the enhanced security features implemented in the EdTech Platform and how to configure them.

## Environment Variables

Add these environment variables to your `.env` file:

```bash
# Enhanced Security Configuration

# IP Whitelisting for Admin Access
# Comma-separated list of allowed IPs, use '*' to allow all IPs
ADMIN_ALLOWED_IPS=127.0.0.1,::1,localhost

# Business Hours Configuration
# Set to 'true' to enable business hours restriction for admin access
BUSINESS_HOURS_ENABLED=false

# Business hours (24-hour format)
BUSINESS_START_HOUR=8
BUSINESS_END_HOUR=18

# Business days (0=Sunday, 1=Monday, etc.)
BUSINESS_DAYS=1,2,3,4,5

# Login Attempts
# Maximum failed login attempts before lockout
MAX_LOGIN_ATTEMPTS=5
# Lockout duration in minutes
LOGIN_LOCKOUT_DURATION_MINUTES=15

# Email Verification
# Verification code expiration time (in minutes)
VERIFICATION_CODE_EXPIRES_MINUTES=10
```

## Security Features Implemented

### 1. Multi-Step Authentication
- **Description**: Two-factor authentication using email verification codes
- **Process**: 
  1. User enters email/password
  2. System sends 6-digit verification code to email
  3. User enters code to complete login
- **Configuration**: `VERIFICATION_CODE_EXPIRES_MINUTES=10`

### 2. Complex Password Validation
- **For Admin/Superadmin**: Minimum 12 characters, uppercase, lowercase, numbers, special characters
- **For Other Roles**: Minimum 8 characters
- **Blacklist**: Common passwords like 'admin123', 'password', etc.

### 3. Rate Limiting
- **Login Attempts**: 5 failed attempts = 15-minute lockout
- **API Requests**: 100 requests per 15 minutes per IP
- **Configuration**: 
  - `MAX_LOGIN_ATTEMPTS=5`
  - `LOGIN_LOCKOUT_DURATION_MINUTES=15`

### 4. IP Whitelisting
- **Description**: Restrict admin access to specific IP addresses
- **Configuration**: `ADMIN_ALLOWED_IPS=127.0.0.1,::1,localhost`
- **Wildcard**: Use `*` to allow all IPs

### 5. Business Hours Restriction
- **Description**: Limit admin access to specific hours and days
- **Configuration**:
  - `BUSINESS_HOURS_ENABLED=true`
  - `BUSINESS_START_HOUR=8`
  - `BUSINESS_END_HOUR=18`
  - `BUSINESS_DAYS=1,2,3,4,5`

### 6. Enhanced Route Protection
- **Admin Access Middleware**: Combines role check, IP whitelist, and business hours
- **Tenant Access Control**: Users can only access their own tenant data
- **Role-Based Permissions**: Strict permission enforcement

### 7. User Approval System
- **Pending Users**: New registrations require admin approval
- **Approval Process**: Admin can approve or reject with reason
- **Email Notifications**: Users receive approval/rejection emails

## Security Best Practices

### 1. Password Security
- Use strong, unique passwords for admin accounts
- Regularly rotate passwords
- Never share admin credentials

### 2. IP Security
- Configure IP whitelist for production environments
- Use VPN for remote admin access
- Monitor access logs

### 3. Business Hours
- Enable business hours restriction in production
- Configure appropriate hours for your organization
- Consider timezone differences

### 4. Rate Limiting
- Monitor failed login attempts
- Adjust limits based on usage patterns
- Set up alerts for suspicious activity

### 5. Email Security
- Use secure email providers
- Enable 2FA on email accounts
- Monitor email delivery

## Production Deployment

### 1. Environment Setup
```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with production values
```

### 2. Database Security
- Use strong database passwords
- Enable SSL connections
- Regular backups
- Monitor database access

### 3. Server Security
- Use HTTPS in production
- Configure firewall rules
- Regular security updates
- Monitor server logs

### 4. Monitoring
- Set up logging for security events
- Monitor failed login attempts
- Track admin access patterns
- Set up alerts for suspicious activity

## Troubleshooting

### Common Issues

1. **Admin Access Denied**
   - Check IP whitelist configuration
   - Verify business hours settings
   - Check user role permissions

2. **Email Verification Not Working**
   - Verify email service configuration
   - Check email delivery logs
   - Ensure correct email addresses

3. **Rate Limiting Issues**
   - Check login attempt counters
   - Verify rate limit configuration
   - Monitor for legitimate vs malicious attempts

### Debug Mode
Set `NODE_ENV=development` to enable detailed error messages and logging.

## Security Checklist

- [ ] Configure strong JWT secret
- [ ] Set up email service
- [ ] Configure IP whitelist
- [ ] Enable business hours (if needed)
- [ ] Set up monitoring and alerts
- [ ] Test all security features
- [ ] Document security procedures
- [ ] Train administrators on security features 