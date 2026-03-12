from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from models import db, PatientRecord, log_action

patient_bp = Blueprint("patients", __name__)


@patient_bp.route("/patients")
@login_required
def patients():

    records = PatientRecord.query.all()

    log_action(current_user.username, "Viewed patient records")

    return render_template("patient_records.html", records=records)


@patient_bp.route("/add_patient", methods=["GET", "POST"])
@login_required
def add_patient():

    if request.method == "POST":

        record = PatientRecord(

            patient_id=request.form["patient_id"],
            age=request.form["age"],
            sex=request.form["sex"],
            blood_pressure=request.form["blood_pressure"],
            cholesterol=request.form["cholesterol"],
            fasting_blood_sugar=request.form["fasting_blood_sugar"],
            resting_ecg=request.form["resting_ecg"],
            angina=request.form["angina"]
        )

        db.session.add(record)
        db.session.commit()

        log_action(current_user.username, "Added patient record")

        flash("Patient record added")

        return redirect(url_for("patients.patients"))

    return render_template("add_patient.html")


@patient_bp.route("/update_patient/<int:id>", methods=["POST"])
@login_required
def update_patient(id):

    record = PatientRecord.query.get_or_404(id)

    record.blood_pressure = request.form["blood_pressure"]
    record.cholesterol = request.form["cholesterol"]
    record.last_updated = datetime.utcnow()

    db.session.commit()

    log_action(current_user.username, "Updated patient record")

    flash("Record updated")

    return redirect(url_for("patients.patients"))


@patient_bp.route("/delete_patient/<int:id>")
@login_required
def delete_patient(id):

    if current_user.role != "admin":

        flash("You do not have permission")
        return redirect(url_for("patients.patients"))

    record = PatientRecord.query.get_or_404(id)

    db.session.delete(record)
    db.session.commit()

    log_action(current_user.username, "Deleted patient record")

    flash("Record deleted")

    return redirect(url_for("patients.patients"))