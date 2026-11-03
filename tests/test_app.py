import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")

from app import app


def test_crud():
    c = app.test_client()
    assert c.get("/health").status_code == 200
    c.post("/tambah", data={"nim": "123", "nama": "Budi", "jurusan": "IF"})
    assert b"Budi" in c.get("/").data
    c.post("/ubah/1", data={"nim": "123", "nama": "Budi Baru", "jurusan": "IF"})
    assert b"Budi Baru" in c.get("/").data
    c.post("/hapus/1")
    assert b"Budi Baru" not in c.get("/").data
