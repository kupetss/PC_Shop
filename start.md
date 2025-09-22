python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
venv\Scripts\activate
pip install django
pip install django-filter
pip install Pillow
python manage.py runserver