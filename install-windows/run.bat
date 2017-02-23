call workon venv-win
call cd ../slider
call python manage.py runserver
start "http://127.0.0.1:8000/offline/album/"
