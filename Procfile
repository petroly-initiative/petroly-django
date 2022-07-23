release: python manage.py migrate --noinput
web: gunicorn petroly.wsgi
worker: python manage.py qcluster
worker: python manage.py startbot
worker: python manage.py startnotifier