from flask import Blueprint, jsonify, request

template_bp = Blueprint('template', __name__)

VALID_TEMPLATES = ['minimal', 'corporate', 'creative']

@template_bp.route('/api/select-template', methods=['POST'])
def select_template():
    data = request.get_json()
    template_name = data.get('template')
    
    if not template_name:
        return jsonify({
            'success': False,
            'error': 'Template name is required'
        }), 400
    
    if template_name not in VALID_TEMPLATES:
        return jsonify({
            'success': False,
            'error': f'Invalid template name. Must be one of: {", ".join(VALID_TEMPLATES)}'
        }), 400
    
    try:
        # Here you can add logic to store the selected template
        # For example, save it to a session or database
        return jsonify({
            'success': True,
            'template': template_name,
            'message': f'Successfully selected {template_name} template'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
