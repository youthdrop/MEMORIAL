SMDROPIN — Stockton/Memorial Drop-In MIS
Backend:
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask db init
flask db migrate -m "init"
flask db upgrade
flask initdb
flask run
Frontend:
cd ../frontend
npm install
npm run dev
Login:
admin@stocktonmemorial.org / ChangeMe123!
