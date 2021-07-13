from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from .models import User, TemporaryUser
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import sqlalchemy
import csv

auth = Blueprint('auth', __name__)
provinsi = \
    ["AC Aceh",
     "SU Sumatera Utara",
     "SB Sumatera Barat",
     "RI Riau",
     "JA Jambi",
     "SS Sumatera Selatan",
     "BE Bengkulu",
     "LA Lampung",
     "BB Kepulauan Bangka Belitung",
     "KR Kepulauan Riau",
     "JK DKI Jakarta",
     "JB Jawa Barat",
     "JT Jawa Tengah",
     "YO DI Yogyakarta",
     "JI Jawa Timur",
     "BT Banten",
     "BA Bali",
     "NB Nusa Tenggara Barat",
     "NT Nusa Tenggara Timur",
     "KB Kalimantan Barat",
     "KT Kalimantan Tengah",
     "KS Kalimantan Selatan"]


@auth.route('/reset-password/<int:id>', methods=["GET"])
def resetPassword(id):
    if request.method == "GET":
        if current_user.status != "admin":
            return "<p>Access Denied</p>"
        else:
            user = User.query.get(id)
            user.password = generate_password_hash(f"ppski2021{id}")
            db.session.commit()
            print(f"ppski2021{id}")
            return redirect(url_for('views.displayTable'))

@auth.route("/masuk", methods=["GET", "POST"])
def masuk():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # flash("Successful login. Redirecting to Homepage.", category="successful")
            login_user(user, remember=True)

            if user.status != "admin":
                return redirect(url_for("views.userDashboard"))
            else:
                return redirect(url_for("views.adminDashboard"))

        else:
            flash("Username atau password salah.",
            category="error")

    return render_template("masuk.html", accessing_user=current_user)

@auth.route('/migrate-user')
def migrateUser():
    with open('/Users/johanestarigan/Downloads/tb_anggota_2021-Jul-12_0928/tb_anggota_2021-Jul-12_0928.csv') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for cleaned in spamreader:
            id_ppski = cleaned[15][1:-1]
            kabupaten_kota = cleaned[13][1:-1]
            provinsi = cleaned[12][1:-1]
            nomor_telepon = '0'+ cleaned[7][1:-1]
            nama_lengkap = cleaned[1][1:-1]
            email = cleaned[5][1:-1]
            nama_tempat = cleaned[4][1:-1]
            tempat_mengajar = cleaned[3][1:-1]
            akun_facebook = cleaned[6][1:-1]
            try:
                tempUser = User(status="permanen", nama_lengkap=nama_lengkap, id_ppski=id_ppski, email=email,
                                password=generate_password_hash('ppski2021'), pendidikan=None,
                                tempat_mengajar=tempat_mengajar, nama_tempat=nama_tempat, akun_facebook=akun_facebook,
                                nomor_telepon=nomor_telepon, provinsi=provinsi,
                                kabupaten_kota=kabupaten_kota
                                )
                db.session.add(tempUser)
                db.session.commit()
            except sqlalchemy.exc.IntegrityError:
                db.session.rollback()

    return redirect(url_for("views.home"))

@auth.route('/make-admin/<int:id>')
@login_required
def makeAdmin(id):
    if current_user.id != 1:
        return "<p>Access Denied</p>"

    user = User.query.get(id)
    if user and user.status != 'admin':
        user.status = 'admin'
        db.session.commit()

    return redirect(url_for("views.displayTable"))


@auth.route('/revoke-admin/<int:id>')
@login_required
def revokeAdmin(id):
    if current_user.id != 1:
        return "<p>Access Denied</p>"

    user = User.query.get(id)
    if user and user.status != 'permanen':
        user.status = 'permanen'
        db.session.commit()

    return redirect(url_for("views.displayTable"))

@auth.route('/generate-admin')
def generateAdmin():
    admin = User(status="admin", email="admin@admin.com",password=generate_password_hash("admin"))
    db.session.add(admin)
    db.session.commit()
    flash("Admin user-created")
    return redirect(url_for("views.home"))


@auth.route("/daftar-anggota", methods=["GET", "POST"])
def daftarAnggota():
    if request.method == "POST":
        status = "temporer"
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        nama_lengkap = request.form.get('nama')
        pendidikan = request.form.get('pendidikan')
        tempat_mengajar = request.form.get('sekolah_tempat_mengajar')
        nama_tempat = request.form.get('nama-sekolah-lembaga')
        akun_facebook = request.form.get('akun-facebook')
        nomor_telepon = request.form.get('nomortelepon')
        provinsiInput = request.form.get('provinsi')
        kabupaten_kota = request.form.get('kabkota')
        esai_singkat = request.form.get('esai')
        print(status, email, password1, password2, nama_lengkap, pendidikan,
              tempat_mengajar, akun_facebook, nomor_telepon,
              provinsiInput, kabupaten_kota, esai_singkat)
        try:
            newUser = TemporaryUser(status=status, email=email,
                           password=generate_password_hash(password1), nama_lengkap=nama_lengkap,
                           pendidikan=pendidikan, tempat_mengajar=tempat_mengajar,
                           akun_facebook=akun_facebook, nomor_telepon=nomor_telepon,
                           nama_tempat=nama_tempat,
                           provinsi=provinsiInput, kabupaten_kota=kabupaten_kota,
                           esai_singkat=esai_singkat)

            db.session.add(newUser)
            db.session.commit()
            flash("Berhasil Mendaftar!", category="success")
            return redirect(url_for("auth.telahMendaftar"))

        except sqlalchemy.exc.IntegrityError:
            flash("Akun surel sudah terdaftar di dalam database", category="error")
            return redirect('auth.telahMendaftar')

    return render_template("beranda.html", provinsi=provinsi,  accessing_user=current_user)


@auth.route('/telah-mendaftar', methods=["GET"])
def telahMendaftar():
    return render_template("telah-mendaftar.html", accessing_user=current_user)


@auth.route('/keluar', methods=["GET"])
@login_required
def keluar():
    logout_user()
    return redirect(url_for("auth.masuk"))