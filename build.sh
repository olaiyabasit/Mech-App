#!/bin/bash
set -e

echo "========================================="
echo "Starting custom build script"
echo "========================================="

# Set Django settings
export DJANGO_SETTINGS_MODULE=winki_project.settings.production

# Build Tailwind CSS
echo "Building Tailwind CSS..."
python build_tailwind.py

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput -v 2

# List staticfiles directory to verify
echo "Verifying staticfiles directory..."
ls -la staticfiles/
ls -la staticfiles/css/

echo "========================================="
echo "Build script completed successfully!"
echo "========================================="
