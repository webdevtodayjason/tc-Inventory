"""API Documentation Routes"""
from flask import Blueprint, render_template, send_from_directory, current_app
import os

bp = Blueprint('api_docs', __name__, url_prefix='/api')

@bp.route('/')
def index():
    """API Documentation Home"""
    return render_template('api/index.html')

@bp.route('/docs')
def docs():
    """Main API Documentation"""
    return render_template('api/index.html')

@bp.route('/docs/mobile')
def mobile_docs():
    """Mobile API Documentation"""
    return render_template('api/mobile.html')

@bp.route('/docs/examples')
def api_examples():
    """API Code Examples"""
    return render_template('api/examples.html')

@bp.route('/docs/changelog')
def changelog():
    """API Changelog"""
    return render_template('api/changelog.html')

@bp.route('/docs/postman')
def postman_collection():
    """Download Postman Collection"""
    return send_from_directory(
        os.path.join(current_app.root_path, 'static', 'api'),
        'tc_inventory_api.postman_collection.json',
        as_attachment=True,
        mimetype='application/json'
    )

@bp.route('/docs/postman/environments')
def postman_environments():
    """Download Postman Environments"""
    return send_from_directory(
        os.path.join(current_app.root_path, 'static', 'api'),
        'tc_inventory_environments.postman_environment.json',
        as_attachment=True,
        mimetype='application/json'
    )

@bp.route('/docs/openapi')
def openapi_spec():
    """Download OpenAPI Specification"""
    return send_from_directory(
        os.path.join(current_app.root_path, 'static', 'api'),
        'tc_inventory_api.yaml',
        as_attachment=True,
        mimetype='application/x-yaml'
    )

@bp.route('/docs/openapi.json')
def openapi_spec_json():
    """Download OpenAPI Specification in JSON format"""
    return send_from_directory(
        os.path.join(current_app.root_path, 'static', 'api'),
        'tc_inventory_api.json',
        as_attachment=True,
        mimetype='application/json'
    ) 