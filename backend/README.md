Backend API (SMDROPIN)
Dev:
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask db init
flask db migrate -m "init"
flask db upgrade
flask initdb
flask run
Env:
DATABASE_URL
JWT_SECRET_KEY
CORS_ORIGINS
