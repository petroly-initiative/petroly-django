release: python manage.py migrate --noinput
web: trap '' SIGTERM; gunicorn petroly.wsgi & python manage.py startnotifier & python manage.py startbot & wait -n; kill -SIGTERM -$$; wait
web: python manage.py qcluster