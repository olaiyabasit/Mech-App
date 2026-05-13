web: gunicorn winki_project.wsgi --log-file -
release: python build_tailwind.py && python manage.py collectstatic --noinput && python manage.py migrate
