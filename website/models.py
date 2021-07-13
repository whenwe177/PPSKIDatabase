from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_ppski = db.Column(db.String(150), unique=True)
    # Admin, Temporer, Permanen
    status = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    nama_lengkap = db.Column(db.String(300))
    pendidikan = db.Column(db.String(150))
    tempat_mengajar = db.Column(db.String(150))
    nama_tempat = db.Column((db.String(150)))
    akun_facebook = db.Column(db.String(150))
    nomor_telepon = db.Column(db.String(150))
    provinsi = db.Column(db.String(150))
    kabupaten_kota = db.Column(db.String(150))
    esai_singkat = db.Column(db.String(3000))


class TemporaryUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_ppski = db.Column(db.String(150), unique=True)
    # Admin, Temporer, Permanen
    status = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    nama_lengkap = db.Column(db.String(300))
    pendidikan = db.Column(db.String(150))
    tempat_mengajar = db.Column(db.String(150))
    nama_tempat = db.Column((db.String(150)))
    akun_facebook = db.Column(db.String(150))
    nomor_telepon = db.Column(db.String(150))
    provinsi = db.Column(db.String(150))
    kabupaten_kota = db.Column(db.String(150))
    esai_singkat = db.Column(db.String(3000))

