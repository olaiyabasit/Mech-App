web: gunicorn winki_project.wsgi --log-file -
release: tailwindcss --input theme/static_src/src/styles.css --output theme/static/css/dist/styles.css --minify && python manage.py collectstatic --noinput && python manage.py migrate
