# 🇹🇿 Local Installation Guide - Tanzania

## 🚀 Quick Start for Local Production Deployment

### Step 1: System Preparation

#### Install Ubuntu 22.04 LTS
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3 python3-pip python3-venv git curl wget
```

#### Install PostgreSQL
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE stationery_db;
CREATE USER stationery_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE stationery_db TO stationery_user;
\q
```

#### Install Nginx
```bash
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 2: Application Setup

#### Clone and Setup Project
```bash
# Navigate to project directory
cd /home/user/stationery

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install production requirements
pip install -r requirements_production.txt

# Run production setup script
python production_setup.py
```

#### Configure Environment
```bash
# Create environment file
sudo nano /etc/environment

# Add these lines:
DJANGO_SECRET_KEY='your-very-long-secret-key-here'
DB_NAME='stationery_db'
DB_USER='stationery_user'
DB_PASSWORD='your_secure_password'
DB_HOST='localhost'
DB_PORT='5432'
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT='587'
EMAIL_HOST_USER='your-email@gmail.com'
EMAIL_HOST_PASSWORD='your-app-password'
DEFAULT_FROM_EMAIL='noreply@stationery.co.tz'
```

### Step 3: Database Migration

#### Migrate from SQLite to PostgreSQL
```bash
# Export data from SQLite
python manage.py dumpdata > sqlite_data.json

# Switch to PostgreSQL (production settings already configured)
export DJANGO_SETTINGS_MODULE=stationery_tracker.production_settings

# Apply migrations
python manage.py migrate

# Import data
python manage.py loaddata sqlite_data.json

# Create superuser
python manage.py createsuperuser
```

### Step 4: Static Files and SSL

#### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

#### Generate SSL Certificate
```bash
# Create SSL directory
sudo mkdir -p /etc/ssl/private

# Generate self-signed certificate (for local use)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/stationery.key \
    -out /etc/ssl/certs/stationery.crt \
    -subj "/C=TZ/ST=Dar es Salaam/L=Dar es Salaam/O=Stationery Management/CN=localhost"
```

### Step 5: System Services

#### Setup Gunicorn Service
```bash
# Copy service file
sudo cp stationery.service /etc/systemd/system/

# Create log directory
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable stationery
sudo systemctl start stationery

# Check status
sudo systemctl status stationery
```

#### Setup Nginx
```bash
# Copy Nginx configuration
sudo cp nginx-stationery.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/nginx-stationery.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Backup and Monitoring

#### Setup Backup Script
```bash
# Create backup directory
sudo mkdir -p /home/user/stationery/backups
sudo chown www-data:www-data /home/user/stationery/backups

# Copy backup script
sudo cp backup.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/backup.sh

# Setup cron job for daily backups
sudo crontab -e
# Add this line:
# 0 2 * * * /usr/local/bin/backup.sh
```

#### Setup Log Rotation
```bash
# Create log rotation config
sudo nano /etc/logrotate.d/stationery

# Add this content:
/var/log/gunicorn/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload stationery
    endscript
}
```

### Step 7: Firewall and Security

#### Configure Firewall
```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow local network access
sudo ufw allow from 192.168.0.0/16
sudo ufw allow from 10.0.0.0/8
sudo ufw allow from 172.16.0.0/12
```

### Step 8: Testing

#### Test Application
```bash
# Check if service is running
sudo systemctl status stationery

# Test locally
curl http://localhost:8000

# Test from network
curl http://192.168.1.100
```

#### Access in Browser
```
https://192.168.1.100
```

## 📱 Mobile Access Setup

### Connect Devices to Local Network
1. **Connect to WiFi**: Join your local network
2. **Access URL**: Open browser and go to `https://192.168.1.100`
3. **Accept SSL**: Accept self-signed certificate warning
4. **Login**: Use superuser credentials or create staff accounts

### Progressive Web App (PWA)
The system works as a PWA on mobile devices:
- **Install**: On mobile, tap "Add to Home Screen"
- **Offline**: Works offline for basic functions
- **Fast**: Optimized for mobile performance

## 🔧 Troubleshooting

### Common Issues

#### Service Not Starting
```bash
# Check logs
sudo journalctl -u stationery -f

# Check configuration
python manage.py check --deploy
```

#### Database Connection Issues
```bash
# Test database connection
psql -U stationery_user -h localhost -d stationery_db

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### Nginx Issues
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

#### SSL Certificate Issues
```bash
# Check certificate expiration
openssl x509 -in /etc/ssl/certs/stationery.crt -text -noout

# Regenerate if needed
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/stationery.key \
    -out /etc/ssl/certs/stationery.crt \
    -subj "/C=TZ/ST=Dar es Salaam/L=Dar es Salaam/O=Stationery Management/CN=192.168.1.100"
```

## 📞 Support

### Technical Support
- **Phone**: +255 746 840 409
- **Email**: paul.sanane@gmail.com
- **Remote Support**: Available via TeamViewer

### Emergency Contacts
- **Power Issues**: Contact your electrician
- **Internet Issues**: Contact your ISP
- **Hardware Issues**: Local computer technician

## 🔄 Maintenance

### Daily Tasks
- Check backup completion
- Monitor system performance
- Check error logs

### Weekly Tasks
- System updates
- Security patches
- Performance optimization

### Monthly Tasks
- Database maintenance
- Log cleanup
- Backup verification

## 🎯 Next Steps

1. **Complete Installation**: Follow all steps above
2. **Staff Training**: Train your staff on system usage
3. **Data Migration**: Import existing customer/sales data
4. **Mobile Setup**: Configure mobile devices for staff
5. **SMS Integration**: Setup SMS notifications (optional)
6. **M-Pesa Integration**: Setup payment processing (optional)

Your system is now ready for production use in Tanzania! 🇹🇿
