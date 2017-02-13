call workon venv-win
call cd ../slider
call python manage.py runserver
call start "" http://127.0.0.1/offline/album/
