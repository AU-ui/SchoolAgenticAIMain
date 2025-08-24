# PostgreSQL Manual Fix Guide

## 🔍 Step 1: Check PostgreSQL Installation

### Check if PostgreSQL is installed:
```bash
psql --version
```

### If not installed, download from:
https://www.postgresql.org/download/windows/

## 🔧 Step 2: Find PostgreSQL Service

### Check available services:
```bash
sc query | findstr postgresql
```

### Common service names:
- postgresql-x64-15
- postgresql-x64-14
- postgresql-x64-13
- postgresql

## 🚀 Step 3: Start PostgreSQL Service

### Start the service:
```bash
net start postgresql-x64-15
```

### Or use Services app:
1. Press Win+R, type `services.msc`
2. Find PostgreSQL service
3. Right-click → Start

## 🔐 Step 4: Reset Password

### Method 1: Using pgAdmin (Recommended)
1. Open pgAdmin
2. Connect to server
3. Right-click on "Login/Group Roles" → "postgres"
4. Properties → Definition
5. Set password to: `1234`
6. Save

### Method 2: Using psql (if you can connect)
```bash
psql -U postgres
ALTER USER postgres PASSWORD '1234';
\q
```

### Method 3: Edit pg_hba.conf (Advanced)
1. Find pg_hba.conf file (usually in PostgreSQL data directory)
2. Change line: `host all all 127.0.0.1/32 md5` to `host all all 127.0.0.1/32 trust`
3. Restart PostgreSQL service
4. Connect and set password
5. Change back to `md5`

## 🗄️ Step 5: Create Database

```bash
psql -U postgres -c "CREATE DATABASE school_management;"
```

## ✅ Step 6: Test Connection

```bash
psql -U postgres -d school_management -c "SELECT version();"
```

## 🎯 Quick Commands

```bash
# 1. Start service
net start postgresql-x64-15

# 2. Reset password (if you can connect)
psql -U postgres -c "ALTER USER postgres PASSWORD '1234';"

# 3. Create database
psql -U postgres -c "CREATE DATABASE school_management;"

# 4. Test connection
psql -U postgres -d school_management -c "SELECT version();"
```

## 🆘 Troubleshooting

### Error: "password authentication failed"
- Try connecting without password first
- Check if PostgreSQL is running
- Verify service name

### Error: "connection refused"
- PostgreSQL service not running
- Wrong port (default: 5432)
- Firewall blocking connection

### Error: "database does not exist"
- Create the database manually
- Check database name spelling
