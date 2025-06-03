"""
Publication Style Config Server
Web service for managing publication styles and export coordination
Version: 20250602_000000_0_0_0_001
"""

from flask import Flask, request, jsonify, render_template
from services.style_manager import StyleManager
from services.template_processor import TemplateProcessor
from services.export_coordinator import ExportCoordinator
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

style_manager = StyleManager()
template_processor = TemplateProcessor()
export_coordinator = ExportCoordinator()

@app.route('/')
def index():
    """Main interface for publication style configuration"""
    return render_template('index.html')

@app.route('/api/styles', methods=['GET'])
def get_available_styles():
    """Get list of available publication styles"""
    try:
        styles = style_manager.get_available_styles()
        return jsonify(styles)
    except Exception as e:
        app.logger.error(f"Error getting styles: {str(e)}")
        return jsonify({'error': 'Failed to retrieve styles'}), 500

@app.route('/api/styles/<style_name>', methods=['GET'])
def get_style_config(style_name):
    """Get configuration for specific publication style"""
    try:
        config = style_manager.get_style_config(style_name)
        if config:
            return jsonify(config)
        else:
            return jsonify({'error': 'Style not found'}), 404
    except Exception as e:
        app.logger.error(f"Error getting style config: {str(e)}")
        return jsonify({'error': 'Failed to retrieve style configuration'}), 500

@app.route('/api/styles/<style_name>', methods=['PUT'])
def update_style_config(style_name):
    """Update configuration for specific publication style"""
    try:
        config_data = request.get_json()
        result = style_manager.update_style_config(style_name, config_data)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error updating style config: {str(e)}")
        return jsonify({'error': 'Failed to update style configuration'}), 500

@app.route('/api/template/process', methods=['POST'])
def process_template():
    """Process content with specified publication style"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        style_name = data.get('style', 'default')
        template_type = data.get('template_type', 'article')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        result = template_processor.process_content(content, style_name, template_type)
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Template processing error: {str(e)}")
        return jsonify({'error': 'Template processing failed'}), 500

@app.route('/api/export/coordinate', methods=['POST'])
def coordinate_export():
    """Coordinate export with other services"""
    try:
        data = request.get_json()
        export_config = {
            'content': data.get('content', ''),
            'style': data.get('style', 'default'),
            'format': data.get('format', 'pdf'),
            'target_services': data.get('target_services', []),
            'export_options': data.get('export_options', {})
        }
        
        result = export_coordinator.coordinate_export(export_config)
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Export coordination error: {str(e)}")
        return jsonify({'error': 'Export coordination failed'}), 500

@app.route('/api/styles/validate', methods=['POST'])
def validate_style():
    """Validate publication style configuration"""
    try:
        style_data = request.get_json()
        validation_result = style_manager.validate_style(style_data)
        return jsonify(validation_result)
    
    except Exception as e:
        app.logger.error(f"Style validation error: {str(e)}")
        return jsonify({'error': 'Style validation failed'}), 500

@app.route('/api/templates/<template_name>', methods=['GET'])
def get_template(template_name):
    """Get specific template configuration"""
    try:
        template = template_processor.get_template(template_name)
        if template:
            return jsonify(template)
        else:
            return jsonify({'error': 'Template not found'}), 404
    except Exception as e:
        app.logger.error(f"Error getting template: {str(e)}")
        return jsonify({'error': 'Failed to retrieve template'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'publication-style-config-server'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)