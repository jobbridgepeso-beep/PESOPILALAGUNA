"""Standard API response helpers."""

from flask import jsonify


def api_ok(data=None, message="Success", status=200):
    return jsonify({"success": True, "data": data, "message": message}), status


def api_err(message="Error", status=400, data=None):
    return jsonify({"success": False, "data": data, "message": message}), status
