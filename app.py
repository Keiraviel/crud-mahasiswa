import os
import sqlite3
from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)
DB = os.environ.get("DB_PATH", "/data/mahasiswa.db")


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS mahasiswa ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "nim TEXT NOT NULL, nama TEXT NOT NULL, jurusan TEXT NOT NULL)"
    )
    conn.commit()
    conn.close()


init_db()

PAGE = """
<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CRUD Mahasiswa</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:"Segoe UI",Tahoma,sans-serif;background:#f1f5f9;color:#1e293b}
header{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:32px 16px;text-align:center}
header h1{margin:0 0 6px;font-size:28px}
header p{margin:0;opacity:.9}
main{max-width:900px;margin:-24px auto 40px;padding:0 16px}
.card{background:#fff;border-radius:14px;padding:20px;margin-bottom:20px;box-shadow:0 4px 14px rgba(15,23,42,.08)}
.card h3{margin:0 0 14px;font-size:18px;color:#4f46e5}
.row{display:flex;flex-wrap:wrap;gap:10px}
input{flex:1;min-width:150px;padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px;font-size:15px}
input:focus{outline:none;border-color:#4f46e5;box-shadow:0 0 0 3px rgba(79,70,229,.15)}
button,.btn{padding:10px 16px;border:0;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;color:#fff;text-decoration:none;display:inline-block}
.primary{background:#4f46e5}.primary:hover{background:#4338ca}
.warn{background:#f59e0b}.warn:hover{background:#d97706}
.danger{background:#ef4444}.danger:hover{background:#dc2626}
.ghost{background:#e2e8f0;color:#334155}
.top{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:12px}
.badge{background:#e0e7ff;color:#4338ca;padding:6px 14px;border-radius:999px;font-weight:600;font-size:14px}
.wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse}
th{background:#4f46e5;color:#fff;text-align:left;padding:12px;font-size:14px}
th:first-child{border-radius:8px 0 0 8px}th:last-child{border-radius:0 8px 8px 0}
td{padding:12px;border-bottom:1px solid #e2e8f0}
tr:hover td{background:#f8fafc}
.aksi{display:flex;gap:6px}
form.inline{display:inline;margin:0}
.kosong{text-align:center;color:#64748b;padding:28px}
footer{text-align:center;color:#64748b;font-size:13px;padding-bottom:24px}
</style>
</head>
<body>
<header>
  <h1>CRUD Data Mahasiswa</h1>
  <p>Aplikasi berjalan di dalam container Podman dengan CI/CD</p>
</header>
<main>
  <div class="card">
    <h3>{{ 'Ubah Data' if edit else 'Tambah Data' }}</h3>
    <form method="post" action="{{ url_for('ubah', id=edit['id']) if edit else url_for('tambah') }}">
      <div class="row">
        <input name="nim" placeholder="NIM" required value="{{ edit['nim'] if edit else '' }}">
        <input name="nama" placeholder="Nama" required value="{{ edit['nama'] if edit else '' }}">
        <input name="jurusan" placeholder="Jurusan" required value="{{ edit['jurusan'] if edit else '' }}">
        <button class="primary" type="submit">{{ 'Simpan Perubahan' if edit else 'Tambah' }}</button>
        {% if edit %}<a class="btn ghost" href="/">Batal</a>{% endif %}
      </div>
    </form>
  </div>

  <div class="card">
    <div class="top">
      <form method="get" action="/" style="flex:1">
        <div class="row">
          <input name="q" placeholder="Cari nama / NIM" value="{{ q }}">
          <button class="primary" type="submit">Cari</button>
          {% if q %}<a class="btn ghost" href="/">Reset</a>{% endif %}
        </div>
      </form>
      <span class="badge">Total data: {{ rows|length }}</span>
    </div>
    <div class="wrap">
      <table>
        <tr><th>ID</th><th>NIM</th><th>Nama</th><th>Jurusan</th><th>Aksi</th></tr>
        {% for r in rows %}
        <tr>
          <td>{{ r['id'] }}</td><td>{{ r['nim'] }}</td><td>{{ r['nama'] }}</td><td>{{ r['jurusan'] }}</td>
          <td>
            <div class="aksi">
              <a class="btn warn" href="/?edit={{ r['id'] }}">Ubah</a>
              <form class="inline" method="post" action="{{ url_for('hapus', id=r['id']) }}"
                    onsubmit="return confirm('Yakin hapus?')">
                <button class="danger" type="submit">Hapus</button>
              </form>
            </div>
          </td>
        </tr>
        {% else %}
        <tr><td class="kosong" colspan="5">Belum ada data.</td></tr>
        {% endfor %}
      </table>
    </div>
  </div>
</main>
<footer>UTS Pengembangan dan Operasi - IF-B Pagi</footer>
</body>
</html>
"""


def run(sql, params=()):
    conn = get_db()
    conn.execute(sql, params)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    edit_id = request.args.get("edit")
    conn = get_db()
    q = request.args.get("q", "").strip()
    if q:
        like = "%" + q + "%"
        rows = conn.execute(
            "SELECT * FROM mahasiswa WHERE nama LIKE ? OR nim LIKE ? ORDER BY id",
            (like, like),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM mahasiswa ORDER BY id").fetchall()
    edit = None
    if edit_id:
        edit = conn.execute("SELECT * FROM mahasiswa WHERE id=?", (edit_id,)).fetchone()
    conn.close()
    return render_template_string(PAGE, rows=rows, edit=edit, q=q)


@app.route("/tambah", methods=["POST"])
def tambah():
    run("INSERT INTO mahasiswa (nim, nama, jurusan) VALUES (?,?,?)",
        (request.form["nim"], request.form["nama"], request.form["jurusan"]))
    return redirect(url_for("index"))


@app.route("/ubah/<int:id>", methods=["POST"])
def ubah(id):
    run("UPDATE mahasiswa SET nim=?, nama=?, jurusan=? WHERE id=?",
        (request.form["nim"], request.form["nama"], request.form["jurusan"], id))
    return redirect(url_for("index"))


@app.route("/hapus/<int:id>", methods=["POST"])
def hapus(id):
    run("DELETE FROM mahasiswa WHERE id=?", (id,))
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return "OK", 200
