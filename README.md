# CRUD Mahasiswa (Flask + SQLite + Podman + CI/CD)

Jalankan lokal (PowerShell):
    podman build -t crud-mahasiswa:v1 .
    podman volume create dbdata
    podman run -d --name crud-app -p 8080:5000 -v dbdata:/data crud-mahasiswa:v1
Buka http://localhost:8080
