#!/bin/bash
# Deployment Commands for Stationery Management System
# Tanzania Local Production Setup

echo "🚀 Starting Stationery Management System Deployment"
echo "=================================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root. Use a regular user with sudo privileges."
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "📦 Installing essential packages..."
sudo apt install -y python3 python3-pip python3-venv git curl wget unzip

# Install PostgreSQL
echo "🗄️ Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
echo "🗄️ Creating database and user..."
sudo -u postgres psql -c "CREATE DATABASE stationery_db;"
sudo -u postgres psql -c "CREATE USER stationery_user WITH PASSWORD 'stationery2024';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE stationery_db TO stationery_user;"
sudo -u postgres psql -c "ALTER USER stationery_user CREATEDB;"

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Install Redis for caching
echo "📦 Installing Redis..."
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Create project directory
echo "📁 Creating project directory..."
sudo mkdir -p /var/www/stationery
sudo chown $USER:$USER /var/www/stationery

# Copy project files
echo "📋 Copying project files..."
cp -r /home/user/stationery/* /var/www/stationery/
cd /var/www/stationery

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install production requirements
echo "📦 Installing production requirements..."
pip install -r requirements_production.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
sudo mkdir -p /var/log/gunicorn
sudo mkdir -p /var/www/stationery/logs
sudo mkdir -p /var/www/stationery/backups
sudo mkdir -p /var/www/stationery/media
sudo mkdir -p /etc/ssl/certs
sudo mkdir -p /etc/ssl/private

# Set permissions
echo "🔐 Setting permissions..."
sudo chown -R www-data:www-data /var/www/stationery
sudo chown -R www-data:www-data /var/log/gunicorn
sudo chmod 755 /var/www/stationery
sudo chmod 755 /var/log/gunicorn

# Copy configuration files
echo "⚙️ Copying configuration files..."
sudo cp stationery.service /etc/systemd/system/
sudo cp nginx-stationery.conf /etc/nginx/sites-available/
sudo cp backup.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/backup.sh

# Setup Nginx
echo "🌐 Setting up Nginx..."
sudo ln -s /etc/nginx/sites-available/nginx-stationery.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# Generate SSL certificate
echo "🔐 Generating SSL certificate..."
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/stationery.key \
    -out /etc/ssl/certs/stationery.crt \
    -subj "/C=TZ/ST=Dar es Salaam/L=Dar es Salaam/O=Stationery Management/CN=192.168.1.100"

# Set SSL permissions
sudo chmod 600 /etc/ssl/private/stationery.key
sudo chmod 644 /etc/ssl/certs/stationery.crt

# Setup environment variables
echo "🌍 Setting up environment variables..."
sudo cp .env.production /etc/environment

# Setup log rotation
echo "📋 Setting up log rotation..."
sudo tee /etc/logrotate.d/stationery > /dev/null <<EOF
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
EOF

# Setup firewall
echo "🔥 Setting up firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from 192.168.0.0/16
sudo ufw allow from 10.0.0.0/8
sudo ufw allow from 172.16.0.0/12

# Setup cron job for backup
echo "⏰ Setting up backup cron job..."
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup.sh") | crontab -

# Database migrations
echo "🗄️ Running database migrations..."
export DJANGO_SETTINGS_MODULE=stationery_tracker.production_settings
python manage.py makemigrations
python manage.py migrate

# Create superuser (will prompt for input)
echo "👤 Creating superuser..."
python manage.py createsuperuser

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Enable and start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable stationery
sudo systemctl start stationery
sudo systemctl restart nginx

# Check service status
echo "🔍 Checking service status..."
sudo systemctl status stationery --no-pager -l
sudo systemctl status nginx --no-pager -l

# Test application
echo "🧪 Testing application..."
sleep 5
curl -s http://localhost:8000 > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Application is running successfully!"
else
    echo "❌ Application failed to start. Check logs with: sudo journalctl -u stationery -f"
fi

echo ""
echo "🎉 Deployment completed!"
echo "======================"
echo "📱 Access your system at: https://192.168.1.100"
echo "📋 Next steps:"
echo "1. Open browser and go to https://192.168.1.100"
echo "2. Accept SSL certificate warning"
echo "3. Login with superuser credentials"
echo "4. Create staff accounts"
echo "5. Import existing data if needed"
echo ""
echo "📞 For support: +255 746 840 409"
echo "📧 Email: paul.sanane@gmail.com"
echo ""
echo "🔧 Useful commands:"
echo "  Check logs: sudo journalctl -u stationery -f"
echo "  Restart app: sudo systemctl restart stationery"
echo "  Check status: sudo systemctl status stationery"
echo "  Backup now: sudo /usr/local/bin/backup.sh"
