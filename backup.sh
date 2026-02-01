#!/bin/bash
# Backup script for Stationery Management System

# Configuration
BACKUP_DIR="/home/user/stationery/backups"
DB_NAME="stationery_db"
DB_USER="stationery_user"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/stationery_backup_$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Database backup
echo "Creating database backup..."
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_FILE

# Compress backup
echo "Compressing backup..."
gzip $BACKUP_FILE

# Media files backup
echo "Backing up media files..."
tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" /home/user/stationery/media/

# Upload to cloud (Google Drive - requires rclone)
if command -v rclone &> /dev/null; then
    echo "Uploading to cloud..."
    rclone copy $BACKUP_DIR gdrive:/stationery_backups/
fi

# Clean old backups (keep last 30 days)
echo "Cleaning old backups..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
