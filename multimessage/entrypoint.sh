set -x

if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]
then
    ./wait-for-it/wait-for-it.sh "${DB_HOST}:${DB_PORT}" --timeout=300
fi

python3 manage.py showmigrations --settings multimessage.settings_prod
python3 manage.py makemigrations contacts --settings multimessage.settings_prod --noinput
python3 manage.py migrate -v 3 --settings multimessage.settings_prod --noinput
python3 manage.py collectstatic --settings multimessage.settings_prod --noinput
python3 manage.py createsuperuser --settings multimessage.settings_prod --noinput
python3 manage.py runserver 0.0.0.0:${APP_PORT} --settings multimessage.settings_prod