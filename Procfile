# npm install --prefix frontend && npm run build --prefix frontend && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate

web: gunicorn --timeout=150 backend.payroll_system.wsgi:application --bind 0.0.0.0:$PORT