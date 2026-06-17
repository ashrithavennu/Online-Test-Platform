/**
 * EduAssess — Frontend API Connector
 * Include this script in every HTML page.
 * Usage: const user = await API.login(email, pass)
 */

const API_BASE = 'http://localhost:5000/api';
// ↑ Flask serves both frontend & backend from port 5000
//   so all API calls go to the same origin — no CORS issues.

const API = {

  // ── Auth ───────────────────────────────────
  async login(email, password, role) {
    const payload = { email, password };
    if (role) payload.role = role;
    const res = await _post('/login', payload);
    if (res.user) {
      localStorage.setItem('ea_user', JSON.stringify(res.user));
      if (res.token) localStorage.setItem('ea_token', res.token);
    }
    return res;
  },

  async register(data) {
    const res = await _post('/register', data);
    if (res.user) {
      localStorage.setItem('ea_user', JSON.stringify(res.user));
      if (res.token) localStorage.setItem('ea_token', res.token);
    }
    return res;
  },

  logout() {
    localStorage.removeItem('ea_user');
    localStorage.removeItem('ea_token');
    window.location.href = 'index.html';
  },

  currentUser() {
    const u = localStorage.getItem('ea_user');
    return u ? JSON.parse(u) : null;
  },

  currentToken() {
    return localStorage.getItem('ea_token');
  },

  requireAuth(role = null) {
    const user = this.currentUser();
    if (!user) { window.location.href = 'index.html'; return null; }
    if (role && user.role !== role) { window.location.href = 'index.html'; return null; }
    return user;
  },

  requireAuth(role = null) {
    const user = this.currentUser();
    if (!user) { window.location.href = 'index.html'; return null; }
    if (role && user.role !== role) { window.location.href = 'index.html'; return null; }
    return user;
  },

  // ── Exams ──────────────────────────────────
  async getExams(status = 'open') {
    return _get(`/exams?status=${status}`);
  },

  async getExam(examId) {
    return _get(`/exams/${examId}`);
  },

  async createExam(data) {
    return _post('/exams', data);
  },

  async updateExam(examId, data) {
    return _put(`/exams/${examId}`, data);
  },

  async addQuestion(examId, questionData) {
    return _post(`/exams/${examId}/questions`, questionData);
  },

  // ── Submission ─────────────────────────────
  async submitExam(studentId, examId, answers, timeTaken) {
    return _post('/submit-exam', {
      student_id: studentId,
      exam_id:    examId,
      answers:    answers,
      time_taken: timeTaken
    });
  },

  // ── Results ────────────────────────────────
  async getResults(studentId) {
    return _get(`/results/${studentId}`);
  },

  async getAttempt(attemptId) {
    return _get(`/results/attempt/${attemptId}`);
  },

  async getAllResults() {
    return _get('/admin/all-results');
  },

  async getStudents() {
    return _get('/admin/students');
  },

  async addStudents(students) {
    return _post('/admin/students', { students });
  },

  async bulkAddStudents(csvText) {
    return _post('/admin/students', { csv_text: csvText });
  },

  // ── ML Prediction ──────────────────────────
  async predict(studentId, attemptId) {
    return _post('/predict', { student_id: studentId, attempt_id: attemptId });
  },

  // ── GenAI Report ───────────────────────────
  async generateReport(studentId, attemptId) {
    return _post('/generate-report', { student_id: studentId, attempt_id: attemptId });
  },

  // ── Health ─────────────────────────────────
  async health() {
    return _get('/health');
  }
};

// ── Internal helpers ─────────────────────────

function _getAuthHeaders() {
  const token = API.currentToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function _get(path) {
  try {
    const res = await fetch(API_BASE + path, {
      headers: {
        'Content-Type': 'application/json',
        ..._getAuthHeaders()
      }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error('API GET error', path, e);
    return { error: e.message };
  }
}

async function _post(path, body) {
  try {
    const res = await fetch(API_BASE + path, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ..._getAuthHeaders()
      },
      body: JSON.stringify(body)
    });
    return await res.json();
  } catch (e) {
    console.error('API POST error', path, e);
    return { error: e.message };
  }
}

async function _put(path, body) {
  try {
    const res = await fetch(API_BASE + path, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    return await res.json();
  } catch (e) {
    console.error('API PUT error', path, e);
    return { error: e.message };
  }
}
