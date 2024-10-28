#!/bin/bash

# Định nghĩa biến
BACKUP_DIR="/db"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/database_$DATE.gz"

# Thực hiện backup
mongodump --host "$DATABASE_HOST" --username "$DATABASE_USERNAME" --password "$DATABASE_PASSWORD" --gzip --archive=$BACKUP_FILE

# Xoá backup cũ (chỉ giữ lại 7 ngày)
find $BACKUP_DIR -type f -mtime +7 -name "*.gz" -exec rm {} \;

echo "Backup completed: $BACKUP_FILE"