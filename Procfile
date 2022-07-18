release: python manage.py migrate --noinput
web: gunicorn petroly.wsgi --log-file -
worker: python manage.py qcluster