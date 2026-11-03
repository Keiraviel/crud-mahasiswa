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
<title>CRUD Mahasiswa</title>
<style>
body{font-family:sans-serif;max-width:800px;margin:30px auto;padding:0 16px}
table{width:100%;border-collapse:collapse;margin-top:16px}
th,td{border:1px solid #ccc;padding:8px;text-align:left}
th{background:#eee}
input{padding:6px;margin:4px}
button{padding:6px 12px;cursor:pointer}
form.inline{display:inline}
</style>
</head>
<body>
<h1>CRUD Data Mahasiswa</h1>
<form method="get" action="/">
  <input name="q" placeholder="Cari nama / NIM" value="{{ q }}">
  <button type="submit">Cari</button>
  {% if q %}<a href="/">Reset</a>{% endif %}
</form>
<p><b>Total data: {{ rows|length }}</b></p>
<h3>{{ 'Ubah Data' if edit else 'Tambah Data' }}</h3>
<form method="post" action="{{ url_for('ubah', id=edit['id']) if edit else url_for('tambah') }}">
  <input name="nim" placeholder="NIM" required value="{{ edit['nim'] if edit else '' }}">
  <input name="nama" placeholder="Nama" required value="{{ edit['nama'] if edit else '' }}">
  <input name="jurusan" placeholder="Jurusan" required value="{{ edit['jurusan'] if edit else '' }}">
  <button type="submit">{{ 'Simpan Perubahan' if edit else 'Tambah' }}</button>
  {% if edit %}<a href="/">Batal</a>{% endif %}
</form>
<table>
  <tr><th>ID</th><th>NIM</th><th>Nama</th><th>Jurusan</th><th>Aksi</th></tr>
  {% for r in rows %}
  <tr>
    <td>{{ r['id'] }}</td><td>{{ r['nim'] }}</td><td>{{ r['nama'] }}</td><td>{{ r['jurusan'] }}</td>
    <td>
      <a href="/?edit={{ r['id'] }}">Ubah</a>
      <form class="inline" method="post" action="{{ url_for('hapus', id=r['id']) }}"
            onsubmit="return confirm('Yakin hapus?')">
        <button type="submit">Hapus</button>
      </form>
    </td>
  </tr>
  {% else %}
  <tr><td colspan="5">Belum ada data.</td></tr>
  {% endfor %}
</table>
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
