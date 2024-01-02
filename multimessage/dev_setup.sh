SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

set -o allexport
source ${SCRIPT_DIR}/../.env
set +o allexport
source ${SCRIPT_DIR}/../.venv/bin/activate

python ${SCRIPT_DIR}/manage.py makemigrations --settings multimessage.settings_dev
python ${SCRIPT_DIR}/manage.py migrate --settings multimessage.settings_dev
python ${SCRIPT_DIR}/manage.py runserver 0.0.0.0:8000 --settings multimessage.settings_dev