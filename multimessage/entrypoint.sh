set -x

sleep 5
python3 manage.py showmigrations
python3 manage.py migrate -v 3 --noinput
python3 manage.py collectstatic --noinput
python3 manage.py createsuperuser --noinput
python3 manage.py runserver 0.0.0.0:${APP_PORT}