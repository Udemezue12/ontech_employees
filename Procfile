# npm install --prefix frontend && npm run build --prefix frontend && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate

web: gunicorn payroll_system.wsgi:application --chdir backend --bind 0.0.0.0:$PORT --timeout 150
