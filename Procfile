release: python manage.py migrate --noinput
web: trap '' SIGTERM; gunicorn petroly.wsgi --log-file - & python manage.py qcluster & wait -n; kill -SIGTERM -$$; wait