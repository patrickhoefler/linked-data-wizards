FROM python:2-onbuild
RUN cp ldva/settings.example.py ldva/settings.py
EXPOSE 8000
CMD gunicorn --bind 0.0.0.0:8000 --error-logfile - --access-logfile - ldva.wsgi
