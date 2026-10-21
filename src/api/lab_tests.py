"""
lab_tests.py -- REST API Blueprint for Diagnostic Laboratory & Radiology Testing.
"""
from flask import Blueprint, request, jsonify, session
import models.lab_test as lab_model
import config

lab_tests_bp = Blueprint("lab_tests", __name__)


@lab_tests_bp.route("/lab-tests", methods=["GET"])
def get_lab_tests():
    patient_id = request.args.get("patient_id")
    abnormal_only = request.args.get("abnormal", "0") == "1"

    if patient_id:
        try:
            p_id = int(patient_id)
            tests = lab_model.list_by_patient(p_id)
        except ValueError:
            return jsonify({"error": "Invalid patient_id"}), 400
    elif abnormal_only:
        tests = lab_model.list_abnormal()
    else:
        tests = lab_model.list_all()

    return jsonify(tests), 200


@lab_tests_bp.route("/lab-tests/<int:test_id>", methods=["GET"])
def get_lab_test(test_id):
    test = lab_model.get_by_id(test_id)
    if not test:
        return jsonify({"error": f"Lab test #{test_id} not found"}), 404
    return jsonify(test), 200


@lab_tests_bp.route("/lab-tests", methods=["POST"])
def order_lab_test():
    data = request.get_json() or {}
    user = session.get("username", "doctor")
    new_id = lab_model.order_test(
        patient_id=data.get("patient_id"),
        doctor_id=data.get("doctor_id"),
        test_name=data.get("test_name"),
        category=data.get("category"),
        unit=data.get("unit"),
        ref_min=data.get("ref_min"),
        ref_max=data.get("ref_max"),
        notes=data.get("notes", ""),
        performed_by=user
    )
    test = lab_model.get_by_id(new_id)
    return jsonify({"message": "Lab test ordered successfully", "lab_test": test}), 201


@lab_tests_bp.route("/lab-tests/<int:test_id>/result", methods=["POST"])
def record_test_result(test_id):
    data = request.get_json() or {}
    user = session.get("username", "lab_technician")
    res_val = data.get("result_value")
    notes = data.get("notes", "")

    updated_test = lab_model.record_result(
        test_id=test_id,
        result_value=res_val,
        notes=notes,
        performed_by=user
    )
    return jsonify({
        "message": "Lab result recorded successfully",
        "lab_test": updated_test,
        "abnormal": bool(updated_test.get("abnormal_flag"))
    }), 200


@lab_tests_bp.route("/lab-tests/templates", methods=["GET"])
def get_templates():
    return jsonify({
        "templates": config.LAB_TEST_TEMPLATES,
        "categories": config.LAB_CATEGORIES
    }), 200
