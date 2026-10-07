import os, secrets
from datetime import datetime, timezone
from flask import Flask, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CSS = ':root{--bg:#0a0a0a;--fg:#f4f1e8;--muted:#a7a39a;--line:#2b2a27;--accent:#d7ff3f}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif}header{height:72px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 5vw}header a{color:var(--fg);text-decoration:none}.logo{font-weight:900;letter-spacing:.08em;font-size:13px}main{max-width:1180px;margin:auto}.hero{text-align:center;padding:105px 20px 80px}.eyebrow{font-size:11px;letter-spacing:.16em;color:var(--accent);font-weight:800}.hero h1{font-size:clamp(44px,8vw,92px);line-height:.95;letter-spacing:-.06em;max-width:1000px;margin:22px auto}.hero h1 span{color:var(--accent)}.hero p{max-width:650px;margin:25px auto 35px;color:var(--muted);font-size:18px;line-height:1.6}.btn{display:inline-block;border:0;background:var(--accent);color:#111;padding:15px 22px;border-radius:999px;font-weight:900;text-decoration:none;cursor:pointer}.counter{max-width:600px;margin:55px auto 0;text-align:left}.counter-top{display:flex;align-items:baseline;gap:8px;margin-bottom:12px}.counter-top b{font-size:42px}.counter-top span{color:var(--muted)}.bar{height:10px;background:#222;border-radius:20px;overflow:hidden}.bar i{display:block;height:100%;background:var(--accent);border-radius:20px}.how{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.how>div{padding:35px;border-right:1px solid var(--line)}.how>div:last-child{border:0}.how b{color:var(--accent)}.how p,.join p,.muted{color:var(--muted);line-height:1.6}.join{margin:100px 20px;padding:50px;border:1px solid var(--line);display:grid;grid-template-columns:1fr 1fr;gap:50px}.join h2,.wall h2,.vote h2{font-size:42px;letter-spacing:-.04em;margin:12px 0}.join form{display:flex;flex-direction:column;gap:12px}.join input{background:#111;border:1px solid var(--line);padding:16px;color:white;border-radius:8px}.join small{color:var(--muted);min-height:20px}.wall,.vote{padding:50px 20px}.section-head{display:flex;justify-content:space-between;align-items:end}.section-head span{color:var(--accent);font-size:11px;font-weight:900}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:25px}.grid article{border:1px solid var(--line);padding:18px;display:flex;flex-direction:column;gap:6px}.grid strong{color:var(--accent)}.grid small{color:var(--muted)}.options{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:30px}.option{background:#111;color:white;border:1px solid var(--line);padding:25px;text-align:left;cursor:pointer;min-height:190px}.option:hover{border-color:var(--accent)}.option b,.option span,.option em{display:block}.option b{font-size:24px;color:var(--accent)}.option span{margin:15px 0;color:var(--muted);line-height:1.5}.option em{font-style:normal;font-size:12px}.card-page{min-height:100vh;display:grid;place-items:center;padding:30px}.participant-card{border:1px solid var(--line);padding:50px;max-width:500px;width:100%;text-align:center}.big{font-size:90px;font-weight:900;letter-spacing:-.08em;margin:20px 0}.badge{border:1px solid var(--accent);color:var(--accent);display:inline-block;padding:8px 12px;margin:25px 0;font-size:11px;letter-spacing:.12em;font-weight:900}footer{text-align:center;border-top:1px solid var(--line);padding:35px;color:var(--muted);font-size:12px}@media(max-width:700px){.how,.join,.options{grid-template-columns:1fr}.how>div{border-right:0;border-bottom:1px solid var(--line)}.grid{grid-template-columns:repeat(2,1fr)}.join{margin:50px 20px;padding:25px}.hero{padding-top:70px}.hero h1{font-size:52px}}\n'

INDEX_HTML = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The $1 Experiment</title><style>{{ CSS|safe }}</style></head><body>\n<header><div class="logo">THE $1 EXPERIMENT</div><a href="#join">Join</a></header>\n<main>\n<section class="hero"><div class="eyebrow">1,000 PEOPLE · $1 EACH · ONE COLLECTIVE DECISION</div><h1>What can <span>1,000 strangers</span> accomplish together?</h1><p>Pay $1 to become a participant. Reach 1,000 people. Then everyone gets one vote on what happens next.</p><a class="btn" href="#join">JOIN FOR $1</a><div class="counter"><div class="counter-top"><b id="count">{{count}}</b><span>/ 1,000 participants</span></div><div class="bar"><i id="bar" style="width:{{ [count/goal*100,100]|min }}%"></i></div></div></section>\n<section class="how"><div><b>01</b><h3>Join</h3><p>Pay $1 and receive your unique participant number.</p></div><div><b>02</b><h3>Bring others</h3><p>Share your participation and help reach 1,000.</p></div><div><b>03</b><h3>Vote</h3><p>Every participant gets one vote when the milestone opens.</p></div></section>\n<section id="join" class="join"><div><div class="eyebrow">BECOME A PARTICIPANT</div><h2>Your $1 gets you in.</h2><p>You\'ll receive a unique participant number, a place on the public wall and one vote. This prototype uses a test payment flow; live payment credentials are added before launch.</p></div><form id="joinForm"><input name="name" placeholder="Name or username" required><input name="country" placeholder="Country" required><input name="email" type="email" placeholder="Email (optional)"><button class="btn" type="submit">PAY $1 & JOIN</button><small id="status"></small></form></section>\n<section class="wall"><div class="section-head"><div><div class="eyebrow">THE PARTICIPANTS</div><h2>Who\'s in?</h2></div><span id="live">LIVE</span></div><div class="grid" id="wall">{% for p in people %}<article><strong>#{{p.public_id}}</strong><span>{{p.name}}</span><small>🌍 {{p.country}}</small></article>{% endfor %}</div></section>\n<section class="vote"><div class="eyebrow">THE DECISION</div><h2>What should happen at 1,000?</h2><p class="muted">Voting is shown for the MVP. In production, voting can be locked until the 1,000-participant milestone.</p><div class="options">{% for key,title,desc in options %}<button class="option" data-option="{{key}}"><b>{{title}}</b><span>{{desc}}</span><em id="v-{{key}}">{{votes[key]}} votes</em></button>{% endfor %}</div></section>\n</main><footer>THE $1 EXPERIMENT · Built as an MVP</footer>\n<script>\nconst form=document.getElementById(\'joinForm\');\nform.addEventListener(\'submit\',async e=>{e.preventDefault();const status=document.getElementById(\'status\');status.textContent=\'Processing test payment…\';const body=Object.fromEntries(new FormData(form));const r=await fetch(\'/api/join\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify(body)});const d=await r.json();if(!r.ok){status.textContent=d.error;return}status.innerHTML=`Success. You\'re <b>#${d.public_id}</b>. <a href="/participant/${d.public_id}">View your card →</a>`;form.reset();refresh();});\nasync function refresh(){const d=await (await fetch(\'/api/stats\')).json();document.getElementById(\'count\').textContent=d.count;document.getElementById(\'bar\').style.width=Math.min(d.count/10,100)+\'%\';const wall=document.getElementById(\'wall\');wall.innerHTML=d.people.map(p=>`<article><strong>#${p.public_id}</strong><span>${escapeHtml(p.name)}</span><small>🌍 ${escapeHtml(p.country)}</small></article>`).join(\'\');for(const k in d.votes){const el=document.getElementById(\'v-\'+k);if(el)el.textContent=d.votes[k]+\' votes\'}}\nfunction escapeHtml(s){return s.replace(/[&<>"\']/g,m=>({\'&\':\'&amp;\',\'<\':\'&lt;\',\'>\':\'&gt;\',\'"\':\'&quot;\',"\'":\'&#039;\'}[m]))}\ndocument.querySelectorAll(\'.option\').forEach(b=>b.addEventListener(\'click\',async()=>{const pid=prompt(\'Enter your participant number (e.g. 0001):\');if(!pid)return;const r=await fetch(\'/api/vote\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({public_id:pid,option:b.dataset.option})});const d=await r.json();alert(d.ok?\'Vote recorded!\':d.error);if(d.ok)refresh()}));\nsetInterval(refresh,5000);\n</script></body></html>\n'

PARTICIPANT_HTML = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Participant #{{p.public_id}}</title><style>{{ CSS|safe }}</style></head><body><main class="card-page"><div class="participant-card"><div class="eyebrow">OFFICIAL PARTICIPANT</div><div class="big">#{{p.public_id}}</div><h1>{{p.name}}</h1><p>🌍 {{p.country}}</p><div class="badge">THE $1 EXPERIMENT</div><a class="btn" href="/">BACK TO EXPERIMENT</a></div></main></body></html>\n'


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
    return render_template_string(INDEX_HTML, CSS=CSS, count=count, goal=GOAL, people=people, options=OPTIONS, votes=votes)

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
    return render_template_string(PARTICIPANT_HTML, CSS=CSS, p=p)

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
