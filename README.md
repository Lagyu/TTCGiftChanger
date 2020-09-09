# TTCGiftChanger
TTC gift changer with django

Top trading cycle (TTC) is an algorithm for trading indivisible items without using money.

Lisenced under GNU General Public Lisence Version 3.

Templates are written in Japanese.

# Setup
1. Install Python3.
1. Clone this repository.
1. Modify "settngs.py" in ttcgiftchanger directory.
1. Run following commands.
```python
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```

- You can start server with:
```python
python manage.py runserver
```
- You can create admin user (can login from /admin/) with:
```python
python manage.py createsuperuser
```
