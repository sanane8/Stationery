# 🪟 Windows Deployment Guide - Stationery Management System

## 🎯 Windows Production Setup for Tanzania

### 📋 System Requirements

#### **Minimum Requirements:**
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB free space
- **Network**: WiFi or Ethernet connection
- **Processor**: Intel i5 or equivalent

#### **Recommended Setup:**
- **OS**: Windows 11 Pro
- **RAM**: 16GB
- **Storage**: 256GB SSD
- **Network**: Gigabit Ethernet
- **UPS**: 1500VA backup power

---

## 🚀 Quick Installation (5 Steps)

### Step 1: Install Prerequisites

#### **Python Installation:**
1. Download Python 3.8+ from https://python.org
2. Run installer as Administrator
3. ✅ Check "Add Python to PATH"
4. ✅ Check "Install for all users"
5. Click "Install Now"

#### **PostgreSQL Installation:**
1. Download from https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
2. Run installer as Administrator
3. Set password: `stationery2024`
4. Install pgAdmin 4 (optional)
5. Complete installation

### Step 2: Run Deployment Script

#### **Automated Setup:**
1. **Right-click** `deploy_windows.bat`
2. **Select "Run as administrator"**
3. **Follow prompts** (takes 10-15 minutes)
4. **Create superuser** when prompted

#### **Manual Steps (if automated fails):**
```cmd
# 1. Open Command Prompt as Administrator
cd C:\stationery
deploy_windows.bat
```

### Step 3: Database Setup

#### **Using pgAdmin:**
1. Open pgAdmin 4
2. Connect to PostgreSQL server
3. Right-click "Databases" → "Create" → "Database"
4. Name: `stationery_db`
5. Create new user: `stationery_user` with password `stationery2024`
6. Grant all privileges

#### **Using Command Line:**
```cmd
# Open SQL Shell (psql)
CREATE DATABASE stationery_db;
CREATE USER stationery_user WITH PASSWORD 'stationery2024';
GRANT ALL PRIVILEGES ON DATABASE stationery_db TO stationery_user;
\q
```

### Step 4: Start the System

#### **Method 1: Desktop Shortcut**
- Double-click "Stationery System" on desktop

#### **Method 2: Command Line**
```cmd
cd C:\stationery
start_system.bat
```

#### **Method 3: Manual Start**
```cmd
cd C:\stationery
venv\Scripts\activate.bat
set DJANGO_SETTINGS_MODULE=stationery_tracker.production_settings
gunicorn --bind 0.0.0.0:8000 stationery_tracker.wsgi:application
```

### Step 5: Access the System

#### **Local Access:**
```
URL: http://localhost:8000
Login: Use superuser credentials created during setup
```

#### **Network Access:**
1. Find your IP address:
   ```cmd
   ipconfig
   ```
2. Access from other devices:
   ```
   URL: http://[YOUR_IP]:8000
   Example: http://192.168.1.100:8000
   ```

---

## 📱 Mobile & Network Setup

### **Find Your Computer's IP:**
```cmd
ipconfig
# Look for "IPv4 Address" under your network adapter
# Example: 192.168.1.100
```

### **Mobile Access:**
1. **Connect phone/tablet** to same WiFi network
2. **Open browser** (Chrome, Safari, etc.)
3. **Go to**: `http://[YOUR_IP]:8000`
4. **Add to Home Screen** for easy access

### **Network Configuration:**
- **Static IP**: Set static IP for your computer
- **Port Forwarding**: Forward port 8000 on router (if needed)
- **Firewall**: Allow port 8000 through Windows Firewall

---

## 🔧 Configuration Files

### **Production Settings Location:**
```
C:\stationery\stationery_tracker\production_settings.py
```

### **Key Configuration:**
```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'stationery_db',
        'USER': 'stationery_user',
        'PASSWORD': 'stationery2024',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Allowed hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.100', '0.0.0.0']
```

---

## 💾 Backup & Maintenance

### **Manual Backup:**
```cmd
cd C:\stationery
backup.bat
```

### **Automatic Backup (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 2:00 AM
4. Action: Start program
5. Program: `C:\stationery\backup.bat`

### **Backup Location:**
```
C:\stationery\backups\
├── stationery_backup_2024_01_31.zip
├── media_backup_2024_01_31.zip
└── ...
```

---

## 🛠️ Troubleshooting

### **Common Issues:**

#### **Port 8000 Already in Use:**
```cmd
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID [PID_NUMBER] /F
```

#### **Database Connection Error:**
1. Check PostgreSQL service is running
2. Verify database credentials
3. Test connection with pgAdmin

#### **Python Not Found:**
1. Reinstall Python with "Add to PATH" checked
2. Restart computer
3. Run deployment script again

#### **Permission Denied:**
1. Run Command Prompt as Administrator
2. Check folder permissions
3. Ensure antivirus isn't blocking

### **Log Files:**
```
C:\stationery\logs\django.log
C:\stationery\logs\gunicorn.log
```

### **Service Management:**
```cmd
# Check if system is running
netstat -ano | findstr :8000

# Restart system
taskkill /F /IM gunicorn.exe
start_system.bat
```

---

## 🔒 Security Setup

### **Windows Firewall:**
```cmd
# Allow port 8000
netsh advfirewall firewall add rule name="Stationery HTTP" dir=in action=allow protocol=TCP localport=8000

# Check firewall rules
netsh advfirewall firewall show rule name="Stationery HTTP"
```

### **Antivirus Exclusions:**
Add these folders to antivirus exclusions:
- `C:\stationery\venv\`
- `C:\stationery\logs\`
- `C:\stationery\backups\`

### **User Accounts:**
1. Create Windows user for the service
2. Grant necessary permissions
3. Use strong passwords

---

## 📊 Performance Optimization

### **System Optimization:**
1. **SSD Storage**: Use SSD for better performance
2. **RAM**: 16GB recommended for multiple users
3. **Network**: Gigabit Ethernet for faster access
4. **Power Settings**: High performance mode

### **Database Optimization:**
```sql
-- PostgreSQL optimization
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
```

---

## 🚀 Advanced Setup

### **Windows Service Installation:**
1. Download NSSM (Non-Sucking Service Manager)
2. Install as Windows service:
```cmd
nssm install StationerySystem "C:\stationery\start_stationery.bat"
nssm start StationerySystem
```

### **SSL Certificate (HTTPS):**
1. Install OpenSSL
2. Generate self-signed certificate
3. Configure Nginx or Apache as reverse proxy

### **Remote Access:**
1. **VPN**: Setup VPN for secure remote access
2. **TeamViewer**: For remote support
3. **Static IP**: Get static IP from ISP

---

## 📞 Support

### **Technical Support:**
- **Phone**: +255 746 840 409
- **Email**: paul.sanane@gmail.com
- **Remote Support**: TeamViewer available

### **Emergency Support:**
- **System Down**: Call immediately
- **Data Issues**: Call with details
- **Network Problems**: Check local network first

---

## 🎯 Success Checklist

### **Before Going Live:**
- [ ] Python 3.8+ installed with PATH
- [ ] PostgreSQL installed and running
- [ ] Database created and configured
- [ ] Deployment script completed successfully
- [ ] Superuser account created
- [ ] System accessible via browser
- [ ] Mobile devices can connect
- [ ] Backup script tested
- [ ] Firewall configured
- [ ] Staff accounts created

### **After Going Live:**
- [ ] Monitor system performance
- [ ] Check daily backups
- [ ] Review user activity
- [ ] Update software regularly
- [ ] Maintain security updates

---

## 🎉 Ready to Go!

Your Stationery Management System is now ready for Windows deployment in Tanzania!

### **Quick Start:**
1. Run `deploy_windows.bat` as Administrator
2. Follow the prompts
3. Access at `http://localhost:8000`
4. Create staff accounts
5. Start using your professional system!

### **Need Help?**
Call me: +255 746 840 409
Email: paul.sanane@gmail.com

**🇹🇿 Perfect for Tanzanian businesses with Windows environments!**
