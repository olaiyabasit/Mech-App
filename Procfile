web: gunicorn winki_project.wsgi --log-file -
release: python manage.py collectstatic --noinput && python manage.py migrate
