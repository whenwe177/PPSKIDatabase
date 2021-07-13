from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .auth import provinsi, db
from .models import User, TemporaryUser
import json, smtplib, ssl, sqlalchemy

views = Blueprint('views', __name__)

calon_ditolak = set()
calon_diterima = set()

selectedTemporaryID = None
selectedUserID = None

provinsi = provinsi

@views.route('/', methods=["GET", "POST"])
def home():
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

    return render_template("beranda.html", provinsi=provinsi, accessing_user=current_user)


@views.route('/cek-data-anggota', methods=["GET","POST"])
def cekAnggota():
    matching_array = []

    if request.method == "POST":
        keyword = request.form.get('nama').strip()
        matching_array = db.session.query(User).filter(User.nama_lengkap.like(f'%{keyword}%'))

    return render_template("cek-data-anggota.html", matching_array=matching_array,  accessing_user=current_user)


@views.route('/dashboard-navigator')
@login_required
def dashboardNavigator():
    if current_user.status == "admin":
        return redirect(url_for("views.adminDashboard"))
    else:
        return redirect(url_for("views.userDashboard"))


@views.route('/user-dashboard', methods=["GET","POST"])
@login_required
def userDashboard():
    return render_template("user-dashboard.html",  accessing_user=current_user)


@views.route('/edit-profil', methods=["GET", "POST"])
@login_required
def userEdit():
    if request.method == "POST":
        pendidikan = request.form.get("pendidikan")
        tempat_mengajar = request.form.get("sekolah_tempat_mengajar")
        nama_tempat = request.form.get("nama-sekolah-lembaga")
        akun_facebook = request.form.get("akun-facebook")
        nomor_telepon = request.form.get("nomortelepon")
        provinsiParam = request.form.get("provinsi")
        kabupaten_kota = request.form.get("kabkota")
        esai_singkat = request.form.get("esai")

        if not (pendidikan and tempat_mengajar and nama_tempat and akun_facebook \
                and nomor_telepon and provinsiParam and kabupaten_kota):
            flash("Terdapat bagian kosong. Harap mengisi seluruh komponen isian.", category="error")

        else:
            current_user.pendidikan = pendidikan
            current_user.tempat_mengajar = tempat_mengajar
            current_user.nama_tempat = nama_tempat
            current_user.akun_facebook = akun_facebook
            current_user.nomor_telepon = nomor_telepon
            current_user.provinsi = provinsiParam
            current_user.kabupaten_kota = kabupaten_kota
            current_user.esai_singkat = esai_singkat
            db.session.commit()
            flash("Data Anda berhasil di update.")
            return redirect(url_for("views.userDashboard"))
    global provinsi
    return render_template("user-edit.html", paramUser=current_user, provinsi=provinsi,  accessing_user=current_user)


@views.route('/admin-dashboard', methods=["GET","POST"])
def adminDashboard():
    if current_user.status != "admin":
        return "<p>Access Denied</p>"
    if request.method == "POST":
        pass
    return render_template("admin-dashboard.html",  accessing_user=current_user)


@views.route('/table-display', methods=["GET", "POST"])
def displayTable():
    if current_user.status != "admin":
        return "<p>Access Denied</p>"
    else:
        global provinsi
        if request.method == "GET":
            permanen = db.session.query(User)

            return render_template("table.html", permanen=permanen,  accessing_user=current_user, provinsi=provinsi, count=permanen.count())
        else:
            keyword = request.form.get('keyword').strip()
            provinsifilter = request.form.get('provinsifilter').strip()
            matching_array = db.session.query(User).filter(User.nama_lengkap.like(f'%{keyword}%'), User.provinsi.like(f'%{provinsifilter}%'))
            return render_template("table.html", permanen=matching_array, accessing_user=current_user, provinsi=provinsi, count=matching_array.count())



@views.route('/registration-queue', methods=["GET", "POST"])
def registrationQueue():
    if request.method == "GET":
        temporer = db.session.query(TemporaryUser)
        return render_template("registration-queue.html", temporer=temporer,  accessing_user=current_user)

    return render_template("registration-queue.html",  accessing_user=current_user)


@views.route('/select-user', methods=["POST"])
def selectUser():
    global selectedTemporaryID
    data = json.loads(request.data)
    selectedTemporaryID = data["userID"]
    return jsonify({})


@views.route('/review-calon', methods=["GET", "POST"])
def reviewCalon():
    global selectedTemporaryID
    paramUser = TemporaryUser.query.get(selectedTemporaryID)
    return render_template("review-calon.html", paramUser=paramUser, accessing_user=current_user)


@views.route('/delete-user/<int:id>', methods=["GET"])
@login_required
def deleteUser(id):
    if current_user.status != 'admin':
        return "<p>Access Denied</p>"

    user = User.query.get(id)
    matching_array = db.session.query(User).filter(User.nama_lengkap.like(f'%{user.nama_lengkap}%'))
    temp = matching_array[0]
    if user:
        db.session.delete(user)
        db.session.delete(temp)
        db.session.commit()

    return redirect(url_for('views.displayTable'))


@views.route('/tolak-calon', methods=["POST"])
def tolakCalon():
    data = json.loads(request.data)
    deletedId = data["userID"]
    user = TemporaryUser.query.get(deletedId)
    calon_ditolak.add(user.email)
    if user:
        db.session.delete(user)
        db.session.commit()

    return jsonify({})


@views.route('/terima-calon', methods=["POST"])
def terimaAnggota():
    data = json.loads(request.data)
    acceptedId = data["userID"]
    user = TemporaryUser.query.get(acceptedId)
    calon_diterima.add(user.email)
    if user:
        user.status = "direview"
        accepted = User(status="permanen", email=user.email,
                      password=user.password, nama_lengkap=user.nama_lengkap,
                      pendidikan=user.pendidikan, tempat_mengajar=user.tempat_mengajar,
                      akun_facebook=user.akun_facebook, nomor_telepon=user.nomor_telepon,
                      nama_tempat=user.nama_tempat,
                      provinsi=user.provinsi, kabupaten_kota=user.kabupaten_kota,
                      esai_singkat=user.esai_singkat)
        db.session.add(accepted)
        db.session.commit()
        flash("Penerimaan berhasil", category="success")

    return jsonify({})


def addtoSet(email):
    calon_diterima.add(email)


def kirimPesan(email, isAccepted):
    sender = "noreplyppskipusat@gmail.com"
    password = "ppskipusat"
    receive = email

    if isAccepted:
        message = """\
            Subject: Pendaftaran Anggota Baru PPSKI
            \n\n
            Anda diterima sebagai anggota dan data Anda sudah\n
            tercantum dalam database kami. Silakan melakukan\n
            pengecekan dan pembaharuan
            
        """
    else:
        message = """\
            Subject: Pendaftaran Anggota Baru PPSKI
            \n\n
            Anda belum diterima sebagai anggota PPSKI
        """

    context = ssl.create_default_context()
    port = 465

    print("Sending email")

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, receive, message)

    print("Email sent!")


@views.route('/temporary-redirect', methods=["GET"])
def temp():
    print("called")
    return redirect(url_for("views.registrationQueue"))


@views.route('/kirim-hasil-review', methods=["GET"])
def bundleSend():
    global calon_diterima, calon_ditolak

    for user in calon_diterima:
        print(user)
        kirimPesan(email=user, isAccepted=True)

    for user in calon_ditolak:
        print(user)
        kirimPesan(email=user, isAccepted=False)

    calon_diterima = set()
    calon_ditolak = set()

    flash("Pesan telah terkirim", category="success")
    return redirect(url_for("views.adminDashboard"))


@views.route('/ganti-password', methods=["GET","POST"])
@login_required
def gantiPassword():
    if request.method == "POST":
        oldpassword = request.form.get("oldpassword")
        newpassword = request.form.get("newpassword")
        confirmedpassword = request.form.get("confirmedpassword")
        condition = True

        # Check oldpassword
        if not (oldpassword and newpassword and confirmedpassword):
            flash("Terdapat bagian kosong. Harap mengisi seluruh komponen isian.", category="error")

        elif not check_password_hash(current_user.password, oldpassword):
            flash("Password lama salah.", category="error")

        elif newpassword != confirmedpassword:
            flash("Konfirmasi password tidak sesuai", category="error")

        elif not condition:
            pass    # Check for condition

        else:
            current_user.password = generate_password_hash(newpassword)
            db.session.commit()
            flash("Password berhasil diganti!")
            return redirect(url_for("views.userDashboard"))

    return render_template("ganti-password.html", paramUser=current_user, accessing_user=current_user)


@views.route('/admin-select-user', methods=["POST"])
def adminSelectedUser():
    global selectedUserID
    if request.method == "POST":
        data = json.loads(request.data)
        selectedUserID = data["userID"]
        return jsonify({})


@views.route('/admin-edit-user/<int:id>', methods=["GET","POST"])
def adminEditUser(id):
    paramUser = User.query.get(id)

    if request.method == "GET":
        return render_template(f"admin-user-edit.html", paramUser=paramUser, provinsi=provinsi,  accessing_user=current_user)

    elif request.method == "POST":
        pendidikan = request.form.get("pendidikan")
        tempat_mengajar = request.form.get("sekolah_tempat_mengajar")
        nama_tempat = request.form.get("nama-sekolah-lembaga")
        akun_facebook = request.form.get("akun-facebook")
        nomor_telepon = request.form.get("nomortelepon")
        provinsiParam = request.form.get("provinsi")
        kabupaten_kota = request.form.get("kabkota")
        esai_singkat = request.form.get("esai")

        if not (pendidikan and tempat_mengajar and nama_tempat and akun_facebook
                and nomor_telepon and provinsiParam and kabupaten_kota):
            flash("Terdapat bagian kosong. Harap mengisi seluruh komponen isian.", category="error")

        else:
            paramUser.pendidikan = pendidikan
            paramUser.tempat_mengajar = tempat_mengajar
            paramUser.nama_tempat = nama_tempat
            paramUser.akun_facebook = akun_facebook
            paramUser.nomor_telepon = nomor_telepon
            paramUser.provinsi = provinsiParam
            paramUser.kabupaten_kota = kabupaten_kota
            paramUser.esai_singkat = esai_singkat
            db.session.commit()
            flash("Data Anda berhasil di update.")
            return redirect(url_for("views.displayTable"))

    return render_template("admin-user-edit.html", paramUser=paramUser, provinsi=provinsi,  accessing_user=current_user)


@views.route('/id-cek-data/<int:id>')
def id_cek_data(id):
    user = User.query.get(id)
    return render_template("id-cek-data.html", user=user,  accessing_user=current_user)