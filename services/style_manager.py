"""
Style Manager Service
Manages publication styles and configurations
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class StyleManager:
    """Service for managing publication styles"""
    
    def __init__(self):
        self.styles_directory = 'styles/journal_templates'
        self.default_styles = self._initialize_default_styles()
        self._ensure_styles_directory()
        self._create_default_style_files()
    
    def _initialize_default_styles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize default publication styles"""
        return {
            'ieee': {
                'name': 'IEEE',
                'description': 'Institute of Electrical and Electronics Engineers style',
                'font_family': 'Times New Roman',
                'font_size': '10pt',
                'line_spacing': '1.0',
                'column_count': 2,
                'page_margins': {
                    'top': '0.75in',
                    'bottom': '1in',
                    'left': '0.625in',
                    'right': '0.625in'
                },
                'header_styles': {
                    'title': {
                        'font_size': '14pt',
                        'font_weight': 'bold',
                        'alignment': 'center',
                        'spacing_after': '12pt'
                    },
                    'author': {
                        'font_size': '12pt',
                        'font_weight': 'normal',
                        'alignment': 'center',
                        'spacing_after': '6pt'
                    },
                    'abstract': {
                        'font_size': '9pt',
                        'font_weight': 'bold',
                        'alignment': 'justify',
                        'indent': '0.25in'
                    }
                },
                'section_styles': {
                    'heading1': {
                        'font_size': '10pt',
                        'font_weight': 'bold',
                        'alignment': 'left',
                        'numbering': 'roman_upper',
                        'spacing_before': '12pt',
                        'spacing_after': '6pt'
                    },
                    'heading2': {
                        'font_size': '10pt',
                        'font_weight': 'bold',
                        'alignment': 'left',
                        'numbering': 'alpha_upper',
                        'spacing_before': '6pt',
                        'spacing_after': '3pt'
                    }
                },
                'reference_style': {
                    'format': 'ieee_numeric',
                    'font_size': '9pt',
                    'hanging_indent': '0.25in'
                },
                'figure_caption': {
                    'prefix': 'Fig.',
                    'font_size': '9pt',
                    'alignment': 'center',
                    'spacing_before': '6pt'
                },
                'table_caption': {
                    'prefix': 'TABLE',
                    'font_size': '9pt',
                    'alignment': 'center',
                    'spacing_after': '6pt'
                }
            },
            'nature': {
                'name': 'Nature',
                'description': 'Nature journal publication style',
                'font_family': 'Times New Roman',
                'font_size': '12pt',
                'line_spacing': '1.5',
                'column_count': 1,
                'page_margins': {
                    'top': '1in',
                    'bottom': '1in',
                    'left': '1in',
                    'right': '1in'
                },
                'header_styles': {
                    'title': {
                        'font_size': '16pt',
                        'font_weight': 'bold',
                        'alignment': 'left',
                        'spacing_after': '18pt'
                    },
                    'author': {
                        'font_size': '12pt',
                        'font_weight': 'normal',
                        'alignment': 'left',
                        'spacing_after': '12pt'
                    },
                    'abstract': {
                        'font_size': '11pt',
                        'font_weight': 'normal',
                        'alignment': 'justify',
                        'spacing_after': '18pt'
                    }
                },
                'section_styles': {
                    'heading1': {
                        'font_size': '14pt',
                        'font_weight': 'bold',
                        'alignment': 'left',
                        'numbering': 'none',
                        'spacing_before': '18pt',
                        'spacing_after': '12pt'
                    },
                    'heading2': {
                        'font_size': '12pt',
                        'font_weight': 'bold',
                        'alignment': 'left',
                        'numbering': 'none',
                        'spacing_before': '12pt',
                        'spacing_after': '6pt'
                    }
                },
                'reference_style': {
                    'format': 'nature_numeric',
                    'font_size': '10pt',
                    'hanging_indent': '0.5in'
                },
                'figure_caption': {
                    'prefix': 'Figure',
                    'font_size': '10pt',
                    'alignment': 'left',
                    'spacing_before': '6pt'
                },
                'table_caption': {
                    'prefix': 'Table',
                    'font_size': '10pt',
                    'alignment': 'left',
                    'spacing_after': '6pt'
                }
            },
            'apa': {
                'name': 'APA',
                'description': 'American Psychological Association style',
                'font_family': 'Times New Roman',
                'font_size': '12pt',
                'line_spacing': '2.0',
                'column_count': 1,
                'page_margins': {
                    'top': '1in',
                    'bottom': '1in',
                    'left': '1in',
                    'right': '1in'
                },
                'header_styles': {
                    'title': {
                        'font_size': '12pt',
                        'font_weight': 'bold',
                        'alignment': 'center',
                        'spacing_after': '12pt'
                    },
                    'author': {
                        'font_size': '12pt',
                        'font_weight': 'normal',
                        'alignment': 'center',
                        'spacing_after': '12pt'
                    },
                    'abstract': {
                        'font_size': '12pt',
                        'font_weight': 'normal',
                        'alignment': 'justify',
                        'spacing_after': '12pt'
                    }
                },
                'section_styles': {
                    'heading1': {
                        'font_size': '12pt',
                        'font_weight': 'bold',
                        'alignment': 'center',
                        'numbering': 'none',
                        'spacing_before': '12pt',
                        'spacing_after': '12pt'
                    },
                    'heading2': {
                        'font_size': '12pt',
                        'font_weight': 'bold',
                        'alignment': 'left',
                        'numbering': 'none',
                        'spacing_before': '12pt',
                        'spacing_after': '6pt'
                    }
                },
                'reference_style': {
                    'format': 'apa',
                    'font_size': '12pt',
                    'hanging_indent': '0.5in'
                },
                'figure_caption': {
                    'prefix': 'Figure',
                    'font_size': '12pt',
                    'alignment': 'left',
                    'spacing_before': '6pt'
                },
                'table_caption': {
                    'prefix': 'Table',
                    'font_size': '12pt',
                    'alignment': 'left',
                    'spacing_after': '6pt'
                }
            }
        }
    
    def _ensure_styles_directory(self):
        """Ensure styles directory exists"""
        os.makedirs(self.styles_directory, exist_ok=True)
    
    def _create_default_style_files(self):
        """Create default style configuration files"""
        for style_name, config in self.default_styles.items():
            file_path = os.path.join(self.styles_directory, f'{style_name}.json')
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(config, f, indent=2)
    
    def get_available_styles(self) -> Dict[str, Any]:
        """Get list of available publication styles"""
        available_styles = {}
        
        # Add default styles
        for style_name, config in self.default_styles.items():
            available_styles[style_name] = {
                'name': config['name'],
                'description': config['description'],
                'source': 'default'
            }
        
        # Add custom styles from files
        if os.path.exists(self.styles_directory):
            for filename in os.listdir(self.styles_directory):
                if filename.endswith('.json'):
                    style_name = filename[:-5]  # Remove .json extension
                    if style_name not in available_styles:
                        try:
                            with open(os.path.join(self.styles_directory, filename), 'r') as f:
                                config = json.load(f)
                                available_styles[style_name] = {
                                    'name': config.get('name', style_name),
                                    'description': config.get('description', 'Custom style'),
                                    'source': 'custom'
                                }
                        except Exception:
                            continue
        
        return {
            'styles': available_styles,
            'count': len(available_styles),
            'metadata': {
                'timestamp': self._get_timestamp(),
                'service': 'style_manager'
            }
        }
    
    def get_style_config(self, style_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific publication style"""
        # Check default styles first
        if style_name in self.default_styles:
            config = self.default_styles[style_name].copy()
            config['metadata'] = {
                'timestamp': self._get_timestamp(),
                'source': 'default',
                'style_name': style_name
            }
            return config
        
        # Check custom style files
        file_path = os.path.join(self.styles_directory, f'{style_name}.json')
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                    config['metadata'] = {
                        'timestamp': self._get_timestamp(),
                        'source': 'custom',
                        'style_name': style_name
                    }
                    return config
            except Exception:
                return None
        
        return None
    
    def update_style_config(self, style_name: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration for specific publication style"""
        # Add metadata to config
        config_data['metadata'] = {
            'timestamp': self._get_timestamp(),
            'last_modified': self._get_timestamp(),
            'style_name': style_name,
            'source': 'custom'
        }
        
        # Save to file
        file_path = os.path.join(self.styles_directory, f'{style_name}.json')
        try:
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return {
                'success': True,
                'message': f'Style {style_name} updated successfully',
                'style_name': style_name,
                'timestamp': self._get_timestamp()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to update style: {str(e)}',
                'style_name': style_name,
                'timestamp': self._get_timestamp()
            }
    
    def validate_style(self, style_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate publication style configuration"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'timestamp': self._get_timestamp()
        }
        
        # Required fields
        required_fields = ['name', 'font_family', 'font_size', 'line_spacing']
        for field in required_fields:
            if field not in style_data:
                validation_results['errors'].append(f'Missing required field: {field}')
                validation_results['valid'] = False
        
        # Font size validation
        if 'font_size' in style_data:
            font_size = style_data['font_size']
            if isinstance(font_size, str) and not font_size.endswith('pt'):
                validation_results['warnings'].append('Font size should include unit (e.g., "12pt")')
        
        # Line spacing validation
        if 'line_spacing' in style_data:
            try:
                spacing = float(style_data['line_spacing'])
                if spacing < 0.5 or spacing > 3.0:
                    validation_results['warnings'].append('Line spacing outside recommended range (0.5-3.0)')
            except ValueError:
                validation_results['errors'].append('Line spacing must be a number')
                validation_results['valid'] = False
        
        # Margin validation
        if 'page_margins' in style_data:
            margins = style_data['page_margins']
            required_margins = ['top', 'bottom', 'left', 'right']
            for margin in required_margins:
                if margin not in margins:
                    validation_results['warnings'].append(f'Missing margin: {margin}')
        
        return validation_results
    
    def create_custom_style(self, style_name: str, base_style: str = 'ieee') -> Dict[str, Any]:
        """Create a new custom style based on existing style"""
        base_config = self.get_style_config(base_style)
        if not base_config:
            return {
                'success': False,
                'message': f'Base style {base_style} not found'
            }
        
        # Modify for custom style
        custom_config = base_config.copy()
        custom_config['name'] = style_name
        custom_config['description'] = f'Custom style based on {base_style}'
        
        return self.update_style_config(style_name, custom_config)
    
    def delete_custom_style(self, style_name: str) -> Dict[str, Any]:
        """Delete a custom style"""
        if style_name in self.default_styles:
            return {
                'success': False,
                'message': 'Cannot delete default styles'
            }
        
        file_path = os.path.join(self.styles_directory, f'{style_name}.json')
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return {
                    'success': True,
                    'message': f'Style {style_name} deleted successfully'
                }
            except Exception as e:
                return {
                    'success': False,
                    'message': f'Failed to delete style: {str(e)}'
                }
        else:
            return {
                'success': False,
                'message': 'Style not found'
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()