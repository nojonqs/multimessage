set -x

python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
python3 manage.py createsuperuser --noinput
python3 manage.py runserver 0.0.0.0:${APP_PORT}