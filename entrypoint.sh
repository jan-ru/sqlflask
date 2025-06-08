#!/bin/sh

if [ "$FLASK_ENV" = "development" ]; then
    flask run --host=0.0.0.0 --port=5000
else
    gunicorn --bind 0.0.0.0:5000 app:app
fi