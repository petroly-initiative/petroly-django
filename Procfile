release: python manage.py migrate --noinput
web: gunicorn petroly.wsgi
worker: trap '' SIGTERM; python manage.py startnotifier & python manage.py startbot & python manage.py qcluster & wait -n; kill -SIGTERM -$$;
