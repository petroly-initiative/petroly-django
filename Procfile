release: python manage.py migrate --noinput
web: trap '' SIGTERM; gunicorn petroly.wsgi & python manage.py startbot & python manage.py qcluster & wait -n; kill -SIGTERM -$$; wait
