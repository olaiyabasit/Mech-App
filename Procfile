web: gunicorn winki_project.wsgi --log-file - --access-logfile - --error-logfile - --log-level debug
release: echo "Starting release phase..." && python build_tailwind.py && echo "Build complete, running collectstatic..." && python manage.py collectstatic --noinput -v 2 && echo "Static files collected, running migrations..." && python manage.py migrate && echo "Release phase complete!"
