import os, secrets
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))
db_url = os.environ.get('DATABASE_URL', 'sqlite:///experiment.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql+psycopg://', 1)
elif db_url.startswith('postgresql://'):
    db_url = db_url.replace('postgresql://', 'postgresql+psycopg://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
GOAL = int(os.environ.get('GOAL', '1000'))

OPTIONS = [
    ('create','CREATE','Build something the participants can experience together.'),
    ('give','GIVE','Use the pool for a community-selected giveaway/project.'),
    ('continue','CONTINUE','Use this experiment to launch the next, bigger challenge.'),
]

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(60), nullable=False)
    country = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120))
    payment_ref = db.Column(db.String(120), unique=True)
    paid = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), unique=True, nullable=False)
    option = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)

def count_participants():
    return Participant.query.filter_by(paid=True).count()

def init_db():
    with app.app_context():
        db.create_all()

@app.get('/health')
def health():
    return {'ok': True}

@app.get('/')
def home():
    count = count_participants()
    people = Participant.query.filter_by(paid=True).order_by(Participant.id.desc()).limit(24).all()
    votes = {key: Vote.query.filter_by(option=key).count() for key, _, _ in OPTIONS}
    return render_template('index.html', count=count, goal=GOAL, people=people, options=OPTIONS, votes=votes)

@app.post('/api/join')
def join():
    data = request.get_json(force=True)
    name = (data.get('name') or '').strip()[:60]
    country = (data.get('country') or '').strip()[:60]
    email = (data.get('email') or '').strip()[:120]
    if not name or not country:
        return jsonify(error='Name and country are required.'), 400
    # TEST MODE ONLY: replace this endpoint with Paystack initialization + server-side verification before live payments.
    public_id = f'{count_participants()+1:04d}'
    ref = 'TEST_' + secrets.token_hex(8)
    p = Participant(public_id=public_id, name=name, country=country, email=email,
                    payment_ref=ref, paid=True, created_at=datetime.now(timezone.utc))
    db.session.add(p); db.session.commit()
    return jsonify(ok=True, public_id=public_id, payment_ref=ref, count=count_participants())

@app.get('/api/stats')
def stats():
    people = Participant.query.filter_by(paid=True).order_by(Participant.id.desc()).limit(50).all()
    votes = {key: Vote.query.filter_by(option=key).count() for key, _, _ in OPTIONS}
    return jsonify(count=count_participants(), goal=GOAL,
                   people=[{'public_id':p.public_id,'name':p.name,'country':p.country} for p in people], votes=votes)

@app.post('/api/vote')
def vote():
    data = request.get_json(force=True)
    pid = (data.get('public_id') or '').strip()
    option = data.get('option')
    valid = [x[0] for x in OPTIONS]
    if option not in valid:
        return jsonify(error='Invalid option.'), 400
    p = Participant.query.filter_by(public_id=pid, paid=True).first()
    if not p:
        return jsonify(error='Participant not found.'), 404
    if Vote.query.filter_by(participant_id=p.id).first():
        return jsonify(error='This participant has already voted.'), 409
    db.session.add(Vote(participant_id=p.id, option=option, created_at=datetime.now(timezone.utc)))
    db.session.commit()
    return jsonify(ok=True)

@app.get('/participant/<pid>')
def participant(pid):
    p = Participant.query.filter_by(public_id=pid, paid=True).first()
    if not p:
        return 'Participant not found', 404
    return render_template('participant.html', p=p)

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
