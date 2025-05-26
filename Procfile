npm install --prefix frontend && npm run build --prefix frontend && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
web: gunicorn backend.payroll_system.deploy:application --log-file -
# worker: gunicorn backend.wsgi:application --log-file - --workers 3 --threads 2
# celery: celery -A backend worker --loglevel=info
# beat: celery -A backend beat --loglevel=info