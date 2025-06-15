#!/bin/bash

set -e  # stop script if any command fails

echo "Starting frontend update..."

# Run backend update script
chmod +x /home/admin/housebrain/backend/deployment/scripts/update.sh
/home/admin/housebrain/backend/deployment/scripts/update.sh

# Build frontend
cd /home/admin/housebrain/frontend
npm run build

# Deploy frontend files
sudo rm -rf /var/www/housebrain-frontend/*
sudo cp -r /home/admin/housebrain/frontend/dist/* /var/www/housebrain-frontend/

echo "Frontend update completed successfully."
