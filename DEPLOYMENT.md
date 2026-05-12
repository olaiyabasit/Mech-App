# WInki - Deployment Guide

## 🚀 Production Deployment

WInki is a professional vehicle and alloy wheel refurbishment business management system built with Django 5.2. This guide covers deployment to various platforms.

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL (for production)
- Git

## 🔧 Environment Configuration

### Production Settings

The application uses environment-specific settings:

- `winki_project/settings/development.py` - Local development
- `winki_project/settings/production.py` - Production deployment
- `winki_project/settings/base.py` - Shared configuration

### Required Environment Variables

Create a `.env` file or set these environment variables:

```env
# Django Configuration
DJANGO_SETTINGS_MODULE=winki_project.settings.production
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database Configuration
DATABASE_URL=postgres://username:password@host:port/dbname

# Optional: Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Optional: Storage Configuration (if using cloud storage)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
```

## 🌐 Platform-Specific Deployment

### Railway

Railway is recommended for easy deployment:

1. **Connect Repository:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and connect
   railway login
   railway link
   ```

2. **Configure Environment:**
   - Add PostgreSQL service in Railway dashboard
   - Set environment variables in Railway dashboard
   - Railway will auto-detect Django and use `requirements.txt`

3. **Deploy:**
   ```bash
   railway up
   ```

### Vercel

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Create `vercel.json`:**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "winki_project/wsgi.py",
         "use": "@vercel/python",
         "config": { "maxLambdaSize": "15mb", "runtime": "python3.11" }
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "winki_project/wsgi.py"
       }
     ],
     "env": {
       "DJANGO_SETTINGS_MODULE": "winki_project.settings.production"
     }
   }
   ```

3. **Deploy:**
   ```bash
   vercel --prod
   ```

### Traditional VPS/Server

1. **Setup Environment:**
   ```bash
   # Clone repository
   git clone your-repo-url winki
   cd winki
   
   # Create virtual environment
   python -m venv winki_env
   source winki_env/bin/activate  # Linux/Mac
   # winki_env\Scripts\activate  # Windows
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure Database:**
   ```bash
   # Install PostgreSQL
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   
   # Create database
   sudo -u postgres createdb winki_db
   sudo -u postgres createuser winki_user
   sudo -u postgres psql
   ALTER USER winki_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE winki_db TO winki_user;
   ```

3. **Setup Application:**
   ```bash
   # Set environment variables
   export DJANGO_SETTINGS_MODULE=winki_project.settings.production
   export SECRET_KEY='your-secret-key'
   export DATABASE_URL='postgres://winki_user:your_password@localhost/winki_db'
   export DEBUG=False
   export ALLOWED_HOSTS='your-domain.com'
   
   # Run migrations
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   
   # Collect static files
   python manage.py collectstatic --noinput
   ```

4. **Setup Web Server (Nginx + Gunicorn):**
   ```bash
   # Install Gunicorn
   pip install gunicorn
   
   # Install Nginx
   sudo apt install nginx
   
   # Create Gunicorn service file
   sudo nano /etc/systemd/system/winki.service
   ```

   Service file content:
   ```ini
   [Unit]
   Description=WInki Django Application
   After=network.target
   
   [Service]
   User=your-user
   Group=www-data
   WorkingDirectory=/path/to/winki
   Environment=DJANGO_SETTINGS_MODULE=winki_project.settings.production
   ExecStart=/path/to/winki/winki_env/bin/gunicorn --access-logfile - --workers 3 --bind unix:/path/to/winki/winki.sock winki_project.wsgi:application
   
   [Install]
   WantedBy=multi-user.target
   ```

5. **Configure Nginx:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
   
       location = /favicon.ico { access_log off; log_not_found off; }
       location /static/ {
           root /path/to/winki;
       }
   
       location / {
           include proxy_params;
           proxy_pass http://unix:/path/to/winki/winki.sock;
       }
   }
   ```

## 🔒 Security Considerations

1. **Generate a secure SECRET_KEY:**
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. **Use HTTPS in production:**
   - Enable SSL/TLS certificates (Let's Encrypt recommended)
   - Set `SECURE_SSL_REDIRECT = True` in production settings

3. **Database Security:**
   - Use strong passwords
   - Restrict database access to application server only
   - Regular database backups

## 📊 Post-Deployment Steps

1. **Load Sample Data (Optional):**
   ```bash
   python manage.py populate_sample_data
   ```

2. **Create Admin User:**
   ```bash
   python manage.py createsuperuser
   ```

3. **Test Key Features:**
   - Admin interface: `/admin/`
   - Dashboard: `/dashboard/`
   - Reports: `/reports/`
   - QR Code functionality
   - PDF report generation
   - CSV exports

## 🐛 Troubleshooting

### Common Issues:

1. **CSS Not Loading:**
   - Run `python manage.py collectstatic`
   - Check `STATIC_URL` and `STATIC_ROOT` settings

2. **Database Connection Issues:**
   - Verify `DATABASE_URL` format
   - Check firewall settings
   - Ensure database server is running

3. **QR Code Images Not Working:**
   - Update hardcoded localhost in `apps/jobs/models.py` line 127
   - Use `request.build_absolute_uri()` for dynamic URLs

4. **Permission Errors:**
   - Check file permissions on application directory
   - Verify web server user has access to socket files

## 📈 Performance Optimization

1. **Enable Caching:**
   ```python
   # Add to production settings
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

2. **Database Optimization:**
   - Enable connection pooling
   - Regular database maintenance
   - Monitor slow queries

3. **Static File Optimization:**
   - Use CDN for static files
   - Enable gzip compression
   - Optimize images

## 🔄 Maintenance

1. **Regular Backups:**
   - Database backups (daily recommended)
   - Media files backup
   - Application code backup

2. **Updates:**
   - Regular security updates
   - Django version updates
   - Dependency updates

3. **Monitoring:**
   - Application logs
   - Database performance
   - Server resources

## 📞 Support

For deployment issues or questions:
- Check Django documentation
- Review application logs
- Test functionality in development environment first

---

**WInki Professional** - Vehicle & Alloy Wheel Refurbishment Management System