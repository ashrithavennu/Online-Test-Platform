"""
EduAssess - AI-Enhanced Online Exam System
Flask Backend — app.py

Folder layout expected:
  online test platform/
  ├── Frontend/        HTML + JS files
  ├── Backend/         this file + ml_model/ + genai/
  └── ML/              notebook, dataset, model.pkl
"""

from flask import Flask, request, jsonify, send_from_directory
import sqlite3, hashlib, os, json, csv
from datetime import datetime

# ─── Paths ────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR     = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(ROOT_DIR, 'Frontend')
DB_PATH      = os.path.join(BASE_DIR, 'eduassess.db')

# ─── Flask app ────────────────────────────────
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
app.config['SECRET_KEY'] = 'eduassess-secret-2024'

# ─── Load GenAI module ────────────────────────
try:
    import sys
    sys.path.insert(0, BASE_DIR)
    from genai.report_generator import generate_report as _genai_report
    GENAI_OK = True
    print("✅ GenAI module loaded.")
except Exception as e:
    GENAI_OK = False
    print(f"⚠️  GenAI module not loaded: {e}")

# ─── CORS ─────────────────────────────────────
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

@app.route('/api/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path=''):
    from flask import Response
    r = Response()
    r.headers['Access-Control-Allow-Origin']  = '*'
    r.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    r.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return r

# ─── Serve Frontend ───────────────────────────
@app.route('/')
def home():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_frontend(filename):
    if filename.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    fp = os.path.join(FRONTEND_DIR, filename)
    if os.path.exists(fp):
        return send_from_directory(FRONTEND_DIR, filename)
    return send_from_directory(FRONTEND_DIR, 'index.html')

# ─── DB helpers ───────────────────────────────
def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ─── DB Init ──────────────────────────────────
def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL, last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
            role TEXT DEFAULT 'student', roll_number TEXT,
            department TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, subject TEXT NOT NULL,
            description TEXT, duration_min INTEGER DEFAULT 45,
            total_marks INTEGER DEFAULT 30, created_by INTEGER,
            status TEXT DEFAULT 'draft', created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL, question_text TEXT NOT NULL,
            option_a TEXT, option_b TEXT, option_c TEXT, option_d TEXT,
            correct_ans TEXT NOT NULL, marks INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL, exam_id INTEGER NOT NULL,
            score REAL DEFAULT 0, total_q INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0, wrong INTEGER DEFAULT 0,
            skipped INTEGER DEFAULT 0, time_taken INTEGER DEFAULT 0,
            answers_json TEXT, submitted_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS ml_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER, attempt_id INTEGER,
            score REAL, time_taken INTEGER, num_attempts INTEGER,
            prediction TEXT, confidence REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS ai_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER, attempt_id INTEGER,
            report_text TEXT, source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    db.commit()
    _seed(db)
    db.close()
    print("✅ Database initialised.")

def _seed(db):
    if db.execute("SELECT id FROM users WHERE email='admin@eduassess.com'").fetchone():
        return
    db.execute("INSERT INTO users (first_name,last_name,email,password,role,department) VALUES (?,?,?,?,?,?)",
               ('Prof.','Kumar','admin@eduassess.com', hash_pw('admin123'), 'admin','Computer Science'))
    for fn,ln,em,roll in [('Aarav','Sharma','aarav@student.com','CS2024001'),
                          ('Priya','Reddy','priya@student.com','CS2024002'),
                          ('Rohit','Gupta','rohit@student.com','CS2024003'),
                          ('Sneha','Patel','sneha@student.com','CS2024004')]:
        db.execute("INSERT OR IGNORE INTO users (first_name,last_name,email,password,role,roll_number,department) VALUES (?,?,?,?,?,?,?)",
                   (fn,ln,em,hash_pw('student123'),'student',roll,'Computer Science'))
    db.execute("INSERT OR IGNORE INTO exams (title,subject,description,duration_min,total_marks,created_by,status) VALUES (?,?,?,?,?,?,?)",
               ('Data Structures & Algorithms','Computer Science','Unit 2 MCQ Test',45,30,1,'open'))
    eid = db.execute("SELECT id FROM exams LIMIT 1").fetchone()['id']
    for qt in [('What is the time complexity of binary search?','O(n)','O(log n)','O(n log n)','O(1)','B'),
               ('Which data structure uses LIFO principle?','Queue','Linked List','Stack','Heap','C'),
               ('Worst-case time complexity of QuickSort?','O(n log n)','O(n²)','O(n)','O(log n)','B'),
               ('Which traversal is Left→Root→Right?','Preorder','Postorder','Inorder','Level order','C'),
               ('Which data structure is used for BFS?','Stack','Queue','Heap','Tree','B')]:
        db.execute("INSERT OR IGNORE INTO questions (exam_id,question_text,option_a,option_b,option_c,option_d,correct_ans) VALUES (?,?,?,?,?,?,?)",
                   (eid,*qt))
    db.commit()
    print("✅ Demo data seeded.")

# ══════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════
@app.route('/api/register', methods=['POST'])
def register():
    d = request.get_json()
    if not all(d.get(k) for k in ['first_name','last_name','email','password']):
        return jsonify({'error':'Missing required fields'}), 400
    db = get_db()
    if db.execute("SELECT id FROM users WHERE email=?", (d['email'],)).fetchone():
        db.close(); return jsonify({'error':'Email already registered'}), 409
    db.execute("INSERT INTO users (first_name,last_name,email,password,role,roll_number,department) VALUES (?,?,?,?,?,?,?)",
               (d['first_name'],d['last_name'],d['email'],hash_pw(d['password']),
                d.get('role','student'),d.get('roll_number',''),d.get('department','General')))
    db.commit()
    user = db.execute("SELECT * FROM users WHERE email=?", (d['email'],)).fetchone()
    db.close()
    return jsonify({'message':'Registration successful',
                    'user':{'id':user['id'],'name':f"{user['first_name']} {user['last_name']}",
                            'email':user['email'],'role':user['role']}}), 201

@app.route('/api/login', methods=['POST'])
def login():
    d = request.get_json()
    if not d.get('email') or not d.get('password'):
        return jsonify({'error':'Email and password required'}), 400
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email=? AND password=?",
                      (d['email'], hash_pw(d['password']))).fetchone()
    db.close()
    if not user:
        return jsonify({'error':'Invalid email or password'}), 401
    requested_role = d.get('role')
    if requested_role and user['role'] != requested_role:
        return jsonify({'error':'No account found for this role'}), 403
    return jsonify({'message':'Login successful',
                    'user':{'id':user['id'],'name':f"{user['first_name']} {user['last_name']}",
                            'email':user['email'],'role':user['role'],
                            'roll_number':user['roll_number'],'department':user['department']}})

# ══════════════════════════════════════════════
# EXAMS
# ══════════════════════════════════════════════
@app.route('/api/exams', methods=['GET'])
def get_exams():
    status = request.args.get('status','open')
    db = get_db()
    rows = db.execute("""
        SELECT e.*, u.first_name||' '||u.last_name as created_by_name,
               COUNT(q.id) as question_count
        FROM exams e LEFT JOIN users u ON e.created_by=u.id
        LEFT JOIN questions q ON q.exam_id=e.id
        WHERE e.status=? GROUP BY e.id ORDER BY e.created_at DESC
    """, (status,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/exams/<int:exam_id>', methods=['GET'])
def get_exam(exam_id):
    db = get_db()
    exam = db.execute("SELECT * FROM exams WHERE id=?", (exam_id,)).fetchone()
    if not exam: db.close(); return jsonify({'error':'Exam not found'}), 404
    qs = db.execute("SELECT id,question_text,option_a,option_b,option_c,option_d FROM questions WHERE exam_id=?", (exam_id,)).fetchall()
    db.close()
    return jsonify({'exam':dict(exam), 'questions':[dict(q) for q in qs]})

@app.route('/api/exams', methods=['POST'])
def create_exam():
    d = request.get_json()
    if not all(d.get(k) for k in ['title','subject','created_by']):
        return jsonify({'error':'Missing required fields'}), 400
    db = get_db()
    cur = db.execute("INSERT INTO exams (title,subject,description,duration_min,total_marks,created_by,status) VALUES (?,?,?,?,?,?,?)",
                     (d['title'],d['subject'],d.get('description',''),d.get('duration_min',45),
                      d.get('total_marks',30),d['created_by'],d.get('status','draft')))
    eid = cur.lastrowid
    for q in d.get('questions',[]):
        db.execute("INSERT INTO questions (exam_id,question_text,option_a,option_b,option_c,option_d,correct_ans,marks) VALUES (?,?,?,?,?,?,?,?)",
                   (eid,q['question_text'],q['option_a'],q['option_b'],q['option_c'],q['option_d'],q['correct_ans'],q.get('marks',1)))
    db.commit(); db.close()
    return jsonify({'message':'Exam created','exam_id':eid}), 201

@app.route('/api/exams/<int:exam_id>', methods=['PUT'])
def update_exam(exam_id):
    d = request.get_json()
    db = get_db()
    db.execute("UPDATE exams SET title=?,subject=?,description=?,duration_min=?,total_marks=?,status=? WHERE id=?",
               (d.get('title'),d.get('subject'),d.get('description'),d.get('duration_min'),d.get('total_marks'),d.get('status'),exam_id))
    db.commit(); db.close()
    return jsonify({'message':'Exam updated'})

@app.route('/api/exams/<int:exam_id>/questions', methods=['POST'])
def add_question(exam_id):
    d = request.get_json()
    db = get_db()
    db.execute("INSERT INTO questions (exam_id,question_text,option_a,option_b,option_c,option_d,correct_ans,marks) VALUES (?,?,?,?,?,?,?,?)",
               (exam_id,d['question_text'],d['option_a'],d['option_b'],d['option_c'],d['option_d'],d['correct_ans'],d.get('marks',1)))
    db.commit(); db.close()
    return jsonify({'message':'Question added'}), 201

# ══════════════════════════════════════════════
# SUBMIT EXAM
# ══════════════════════════════════════════════
@app.route('/api/submit-exam', methods=['POST'])
def submit_exam():
    d          = request.get_json()
    student_id = d.get('student_id')
    exam_id    = d.get('exam_id')
    answers    = d.get('answers', {})
    time_taken = d.get('time_taken', 0)
    if not student_id or not exam_id:
        return jsonify({'error':'student_id and exam_id required'}), 400

    db = get_db()
    questions = db.execute("SELECT id,correct_ans,marks FROM questions WHERE exam_id=? ORDER BY id ASC", (exam_id,)).fetchall()
    total_q = len(questions)
    correct = wrong = skipped = 0

    # Support answers keyed by question DB id or by 1-based question position.
    for idx, q in enumerate(questions, start=1):
        sel = answers.get(str(q['id']))
        if sel is None:
            sel = answers.get(str(idx))
        if sel is None:
            skipped += 1
        elif sel.upper() == q['correct_ans'].upper():
            correct += 1
        else:
            wrong += 1

    score_pct = round(correct / total_q * 100, 2) if total_q > 0 else 0
    cur = db.execute("INSERT INTO attempts (student_id,exam_id,score,total_q,correct,wrong,skipped,time_taken,answers_json) VALUES (?,?,?,?,?,?,?,?,?)",
                     (student_id,exam_id,score_pct,total_q,correct,wrong,skipped,time_taken,json.dumps(answers)))
    attempt_id = cur.lastrowid
    db.commit(); db.close()
    return jsonify({'message':'Exam submitted','attempt_id':attempt_id,
                    'result':{'score':score_pct,'correct':correct,'wrong':wrong,
                              'skipped':skipped,'total':total_q,'time_taken':time_taken}})

# ══════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════
@app.route('/api/results/<int:student_id>', methods=['GET'])
def get_results(student_id):
    db = get_db()
    rows = db.execute("""
        SELECT a.*, e.title as exam_title, e.subject
        FROM attempts a JOIN exams e ON a.exam_id=e.id
        WHERE a.student_id=? ORDER BY a.submitted_at DESC
    """, (student_id,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/results/attempt/<int:attempt_id>', methods=['GET'])
def get_attempt(attempt_id):
    db = get_db()
    row = db.execute("""
        SELECT a.*, e.title as exam_title, e.subject,
               u.first_name||' '||u.last_name as student_name
        FROM attempts a JOIN exams e ON a.exam_id=e.id JOIN users u ON a.student_id=u.id
        WHERE a.id=?
    """, (attempt_id,)).fetchone()
    db.close()
    if not row: return jsonify({'error':'Attempt not found'}), 404
    return jsonify(dict(row))

@app.route('/api/admin/all-results', methods=['GET'])
def all_results():
    db = get_db()
    rows = db.execute("""
        SELECT a.id, a.score, a.correct, a.wrong, a.skipped, a.time_taken, a.submitted_at,
               u.first_name||' '||u.last_name as student_name, u.roll_number, e.title as exam_title
        FROM attempts a JOIN users u ON a.student_id=u.id JOIN exams e ON a.exam_id=e.id
        ORDER BY a.submitted_at DESC
    """).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/students', methods=['GET'])
def get_students():
    db = get_db()
    rows = db.execute("""
        SELECT u.id, u.first_name, u.last_name, u.email, u.roll_number, u.department,
               COUNT(a.id) as exam_count, ROUND(AVG(a.score),1) as avg_score
        FROM users u LEFT JOIN attempts a ON a.student_id=u.id
        WHERE u.role='student' GROUP BY u.id ORDER BY u.first_name
    """).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/students', methods=['POST'])
def add_students():
    d = request.get_json() or {}
    students = d.get('students')
    csv_text = d.get('csv_text')
    if csv_text and not students:
        try:
            reader = csv.DictReader(csv_text.strip().splitlines())
            students = [row for row in reader]
        except Exception as exc:
            return jsonify({'error': f'Could not parse CSV: {exc}'}), 400
    if not students:
        required = ['first_name', 'last_name', 'email', 'password']
        if not all(d.get(k) for k in required):
            return jsonify({'error': 'Missing required student fields'}), 400
        students = [{
            'first_name': d.get('first_name'),
            'last_name': d.get('last_name'),
            'email': d.get('email'),
            'password': d.get('password'),
            'roll_number': d.get('roll_number',''),
            'department': d.get('department','General')
        }]
    if not isinstance(students, list):
        return jsonify({'error': 'students must be a list'}), 400
    db = get_db()
    inserted = []
    skipped = []
    for student in students:
        if not all(student.get(k) for k in ['first_name','last_name','email','password']):
            skipped.append({'student': student, 'reason': 'Missing required fields'})
            continue
        if db.execute('SELECT id FROM users WHERE email=?', (student['email'],)).fetchone():
            skipped.append({'student': student, 'reason': 'Email already registered'})
            continue
        db.execute("INSERT INTO users (first_name,last_name,email,password,role,roll_number,department) VALUES (?,?,?,?,?,?,?)",
                   (student['first_name'], student['last_name'], student['email'], hash_pw(student['password']), 'student', student.get('roll_number',''), student.get('department','General')))
        inserted.append({'email': student['email'], 'name': f"{student['first_name']} {student['last_name']}"})
    db.commit()
    db.close()
    return jsonify({'inserted': inserted, 'skipped': skipped, 'total': len(students)})

# ══════════════════════════════════════════════════════════════════════
# ML PREDICTION
# ══════════════════════════════════════════════
@app.route('/api/predict', methods=['POST'])
def predict():
    d          = request.get_json()
    student_id = d.get('student_id')
    attempt_id = d.get('attempt_id')
    if not student_id or not attempt_id:
        return jsonify({'error':'student_id and attempt_id required'}), 400

    db = get_db()
    attempt = db.execute("SELECT * FROM attempts WHERE id=?", (attempt_id,)).fetchone()
    if not attempt: db.close(); return jsonify({'error':'Attempt not found'}), 404

    score      = attempt['score']
    time_taken = attempt['time_taken']
    num_attempts = db.execute("SELECT COUNT(*) as c FROM attempts WHERE student_id=?", (student_id,)).fetchone()['c']
    past_avg   = db.execute("SELECT AVG(score) as avg FROM attempts WHERE student_id=?", (student_id,)).fetchone()['avg'] or score
    db.close()

    # ── Real Decision Tree model ──
    try:
        import pickle, pandas as pd
        model_path = os.path.join(BASE_DIR, 'ml_model', 'model.pkl')
        with open(model_path, 'rb') as f:
            md = pickle.load(f)
        X = pd.DataFrame([[score, time_taken, num_attempts, past_avg]], columns=md['features'])
        prediction = md['label_encoder'].inverse_transform(md['model'].predict(X))[0]
        confidence = round(float(max(md['model'].predict_proba(X)[0])) * 100, 1)
        source     = 'decision_tree_model'
    except Exception as e:
        print(f"ML model error: {e}")
        # Rule-based fallback
        if score >= 75:   prediction, confidence = 'Good Performer',    87.5
        elif score >= 50: prediction, confidence = 'Average Performer', 78.2
        else:             prediction, confidence = 'Needs Improvement', 83.1
        source = 'rule_based_fallback'

    # Store prediction
    db2 = get_db()
    db2.execute("INSERT INTO ml_predictions (student_id,attempt_id,score,time_taken,num_attempts,prediction,confidence) VALUES (?,?,?,?,?,?,?)",
                (student_id,attempt_id,score,time_taken,num_attempts,prediction,confidence))
    db2.commit(); db2.close()

    return jsonify({'prediction':prediction,'confidence':confidence,'source':source,
                    'features_used':{'score':score,'time_taken_min':time_taken,
                                     'num_attempts':num_attempts,'past_avg_score':round(past_avg,1)}})

# ══════════════════════════════════════════════
# GENAI REPORT
# ══════════════════════════════════════════════
@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    d          = request.get_json()
    student_id = d.get('student_id')
    attempt_id = d.get('attempt_id')
    if not student_id or not attempt_id:
        return jsonify({'error':'student_id and attempt_id required'}), 400

    db = get_db()
    attempt = db.execute("""
        SELECT a.*, e.title as exam_title, e.subject,
               u.first_name||' '||u.last_name as student_name
        FROM attempts a JOIN exams e ON a.exam_id=e.id JOIN users u ON a.student_id=u.id
        WHERE a.id=?
    """, (attempt_id,)).fetchone()
    db.close()
    if not attempt: return jsonify({'error':'Attempt not found'}), 404

    attempt = dict(attempt)
    student_data = {
        'student_name': attempt['student_name'],
        'exam_title':   attempt['exam_title'],
        'subject':      attempt['subject'],
        'score':        attempt['score'],
        'correct':      attempt['correct'],
        'wrong':        attempt['wrong'],
        'skipped':      attempt['skipped'],
        'total':        attempt['total_q'],
        'time_taken':   attempt['time_taken']
    }

    # ── Call GenAI module ──
    if GENAI_OK:
        result = _genai_report(student_data)
    else:
        # inline fallback if module failed to import
        from genai.report_generator import _template_report
        result = _template_report(student_data)

    report_text = result['report']
    sections    = result.get('sections', {})
    source      = result.get('source', 'template')

    # Store report
    db3 = get_db()
    db3.execute("INSERT INTO ai_reports (student_id,attempt_id,report_text,source) VALUES (?,?,?,?)",
                (student_id, attempt_id, report_text, source))
    db3.commit(); db3.close()

    return jsonify({'report':report_text, 'sections':sections, 'source':source,
                    'student_name':attempt['student_name'],
                    'exam_title':attempt['exam_title'], 'score':attempt['score']})

# ══════════════════════════════════════════════
# HEALTH
# ══════════════════════════════════════════════
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status':'running','app':'EduAssess Backend',
                    'version':'1.0.0','genai_loaded':GENAI_OK,
                    'timestamp':datetime.now().isoformat()})

# ══════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════
if __name__ == '__main__':
    init_db()
    print("🚀 EduAssess running at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
