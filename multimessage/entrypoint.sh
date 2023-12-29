set -x

if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]
then
    ./wait-for-it/wait-for-it.sh "${DB_HOST}:${DB_PORT}" --timeout=300
fi

python3 manage.py showmigrations
python3 manage.py migrate -v 3 --noinput
python3 manage.py collectstatic --noinput
python3 manage.py createsuperuser --noinput
python3 manage.py runserver 0.0.0.0:${APP_PORT}