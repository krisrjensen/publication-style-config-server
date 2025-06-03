"""
Export Coordinator Service
Coordinates exports with other services in the ecosystem
"""

import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import aiohttp

class ExportCoordinator:
    """Service for coordinating exports across multiple services"""
    
    def __init__(self):
        self.service_registry = self._initialize_service_registry()
        self.export_formats = self._initialize_export_formats()
        self.coordination_history = []
    
    def _initialize_service_registry(self) -> Dict[str, Dict[str, Any]]:
        """Initialize registry of available services"""
        return {
            'distance_server': {
                'url': 'http://localhost:5001',
                'capabilities': ['distance_calculation', 'visualization', 'data_export'],
                'export_formats': ['json', 'csv', 'excel'],
                'health_endpoint': '/health'
            },
            'styles_gallery': {
                'url': 'http://localhost:4090',
                'capabilities': ['style_management', 'asset_serving', 'preview_generation'],
                'export_formats': ['html', 'css', 'json'],
                'health_endpoint': '/health'
            },
            'style_assets': {
                'url': 'http://localhost:5003',
                'capabilities': ['asset_management', 'font_serving', 'color_schemes'],
                'export_formats': ['zip', 'tar', 'json'],
                'health_endpoint': '/health'
            }
        }
    
    def _initialize_export_formats(self) -> Dict[str, Dict[str, Any]]:
        """Initialize supported export formats and their configurations"""
        return {
            'pdf': {
                'name': 'PDF Document',
                'mime_type': 'application/pdf',
                'requires_latex': True,
                'compatible_styles': ['ieee', 'nature', 'apa'],
                'processing_service': 'publication_style_config_server'
            },
            'docx': {
                'name': 'Microsoft Word Document',
                'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'requires_latex': False,
                'compatible_styles': ['ieee', 'nature', 'apa'],
                'processing_service': 'publication_style_config_server'
            },
            'html': {
                'name': 'HTML Document',
                'mime_type': 'text/html',
                'requires_latex': False,
                'compatible_styles': ['ieee', 'nature', 'apa', 'web'],
                'processing_service': 'styles_gallery'
            },
            'latex': {
                'name': 'LaTeX Source',
                'mime_type': 'text/x-tex',
                'requires_latex': False,
                'compatible_styles': ['ieee', 'nature', 'apa'],
                'processing_service': 'publication_style_config_server'
            },
            'markdown': {
                'name': 'Markdown Document',
                'mime_type': 'text/markdown',
                'requires_latex': False,
                'compatible_styles': ['github', 'basic'],
                'processing_service': 'publication_style_config_server'
            }
        }
    
    def coordinate_export(self, export_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate export across multiple services
        
        Args:
            export_config: Export configuration
            
        Returns:
            Dictionary containing coordination results
        """
        coordination_id = self._generate_coordination_id()
        
        # Validate export configuration
        validation_result = self._validate_export_config(export_config)
        if not validation_result['valid']:
            return {
                'success': False,
                'coordination_id': coordination_id,
                'errors': validation_result['errors'],
                'timestamp': self._get_timestamp()
            }
        
        # Check service availability
        available_services = self._check_service_availability(export_config['target_services'])
        
        # Plan export workflow
        workflow = self._plan_export_workflow(export_config, available_services)
        
        # Execute export workflow
        execution_result = self._execute_export_workflow(workflow, coordination_id)
        
        # Store coordination history
        self._store_coordination_history(coordination_id, export_config, execution_result)
        
        return {
            'success': execution_result['success'],
            'coordination_id': coordination_id,
            'workflow': workflow,
            'results': execution_result,
            'available_services': available_services,
            'timestamp': self._get_timestamp()
        }
    
    def _validate_export_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate export configuration"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Required fields
        required_fields = ['content', 'style', 'format']
        for field in required_fields:
            if field not in config:
                validation_result['errors'].append(f'Missing required field: {field}')
                validation_result['valid'] = False
        
        # Format validation
        if 'format' in config and config['format'] not in self.export_formats:
            validation_result['errors'].append(f'Unsupported export format: {config["format"]}')
            validation_result['valid'] = False
        
        # Style compatibility
        if 'style' in config and 'format' in config:
            format_config = self.export_formats.get(config['format'], {})
            compatible_styles = format_config.get('compatible_styles', [])
            if compatible_styles and config['style'] not in compatible_styles:
                validation_result['warnings'].append(
                    f'Style {config["style"]} may not be compatible with format {config["format"]}'
                )
        
        return validation_result
    
    def _check_service_availability(self, target_services: List[str]) -> Dict[str, Dict[str, Any]]:
        """Check availability of target services"""
        availability = {}
        
        for service_name in target_services:
            if service_name in self.service_registry:
                service_config = self.service_registry[service_name]
                health_status = self._check_service_health(service_config)
                availability[service_name] = {
                    'available': health_status['healthy'],
                    'response_time': health_status.get('response_time', 0),
                    'capabilities': service_config['capabilities'],
                    'url': service_config['url']
                }
            else:
                availability[service_name] = {
                    'available': False,
                    'error': 'Service not found in registry'
                }
        
        return availability
    
    def _check_service_health(self, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of individual service"""
        try:
            import time
            start_time = time.time()
            
            response = requests.get(
                f"{service_config['url']}{service_config['health_endpoint']}",
                timeout=5
            )
            
            response_time = time.time() - start_time
            
            return {
                'healthy': response.status_code == 200,
                'response_time': response_time,
                'status_code': response.status_code
            }
        
        except requests.RequestException:
            return {
                'healthy': False,
                'response_time': None,
                'error': 'Connection failed'
            }
    
    def _plan_export_workflow(self, export_config: Dict[str, Any], 
                             available_services: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Plan export workflow based on configuration and available services"""
        workflow = []
        export_format = export_config['format']
        format_config = self.export_formats[export_format]
        
        # Step 1: Content preprocessing
        workflow.append({
            'step': 1,
            'action': 'preprocess_content',
            'service': 'publication_style_config_server',
            'description': 'Process content with style and template',
            'inputs': {
                'content': export_config['content'],
                'style': export_config['style'],
                'template_type': export_config.get('template_type', 'article')
            }
        })
        
        # Step 2: Asset coordination (if style assets needed)
        if 'style_assets' in available_services and available_services['style_assets']['available']:
            workflow.append({
                'step': 2,
                'action': 'coordinate_assets',
                'service': 'style_assets',
                'description': 'Gather required style assets',
                'inputs': {
                    'style': export_config['style'],
                    'format': export_format
                }
            })
        
        # Step 3: Format-specific processing
        processing_service = format_config.get('processing_service', 'publication_style_config_server')
        workflow.append({
            'step': 3,
            'action': 'format_conversion',
            'service': processing_service,
            'description': f'Convert to {export_format} format',
            'inputs': {
                'processed_content': 'from_step_1',
                'assets': 'from_step_2' if len(workflow) > 1 else None,
                'format': export_format,
                'export_options': export_config.get('export_options', {})
            }
        })
        
        # Step 4: Quality validation
        workflow.append({
            'step': 4,
            'action': 'validate_output',
            'service': 'publication_style_config_server',
            'description': 'Validate export quality and completeness',
            'inputs': {
                'exported_content': 'from_step_3',
                'validation_rules': export_config.get('validation_rules', {})
            }
        })
        
        return workflow
    
    def _execute_export_workflow(self, workflow: List[Dict[str, Any]], 
                                coordination_id: str) -> Dict[str, Any]:
        """Execute export workflow"""
        execution_result = {
            'success': True,
            'steps_completed': 0,
            'step_results': [],
            'errors': [],
            'final_output': None
        }
        
        step_outputs = {}
        
        for step in workflow:
            try:
                step_result = self._execute_workflow_step(step, step_outputs, coordination_id)
                
                execution_result['step_results'].append({
                    'step': step['step'],
                    'action': step['action'],
                    'service': step['service'],
                    'success': step_result['success'],
                    'output': step_result.get('output'),
                    'execution_time': step_result.get('execution_time'),
                    'timestamp': self._get_timestamp()
                })
                
                if step_result['success']:
                    execution_result['steps_completed'] += 1
                    step_outputs[f"step_{step['step']}"] = step_result['output']
                    
                    # Store final output if this is the last step
                    if step['step'] == len(workflow):
                        execution_result['final_output'] = step_result['output']
                else:
                    execution_result['success'] = False
                    execution_result['errors'].append(
                        f"Step {step['step']} failed: {step_result.get('error', 'Unknown error')}"
                    )
                    break
            
            except Exception as e:
                execution_result['success'] = False
                execution_result['errors'].append(f"Step {step['step']} execution failed: {str(e)}")
                break
        
        return execution_result
    
    def _execute_workflow_step(self, step: Dict[str, Any], 
                              step_outputs: Dict[str, Any], 
                              coordination_id: str) -> Dict[str, Any]:
        """Execute individual workflow step"""
        import time
        start_time = time.time()
        
        # Mock implementation - in real scenario, this would make actual service calls
        # For now, return success with mock data
        
        if step['action'] == 'preprocess_content':
            return {
                'success': True,
                'output': {
                    'processed_content': f"Processed content with style {step['inputs']['style']}",
                    'sections': ['title', 'abstract', 'introduction', 'conclusion'],
                    'word_count': 2500,
                    'style_applied': step['inputs']['style']
                },
                'execution_time': time.time() - start_time
            }
        
        elif step['action'] == 'coordinate_assets':
            return {
                'success': True,
                'output': {
                    'fonts': ['times-new-roman', 'arial'],
                    'color_scheme': 'academic_blue',
                    'templates': ['ieee_template.css'],
                    'asset_count': 15
                },
                'execution_time': time.time() - start_time
            }
        
        elif step['action'] == 'format_conversion':
            return {
                'success': True,
                'output': {
                    'format': step['inputs']['format'],
                    'file_size': '1.2MB',
                    'pages': 8,
                    'conversion_quality': 'high',
                    'download_url': f'/exports/{coordination_id}/output.{step["inputs"]["format"]}'
                },
                'execution_time': time.time() - start_time
            }
        
        elif step['action'] == 'validate_output':
            return {
                'success': True,
                'output': {
                    'validation_passed': True,
                    'quality_score': 0.95,
                    'issues_found': 0,
                    'recommendations': []
                },
                'execution_time': time.time() - start_time
            }
        
        else:
            return {
                'success': False,
                'error': f"Unknown action: {step['action']}",
                'execution_time': time.time() - start_time
            }
    
    def _store_coordination_history(self, coordination_id: str, 
                                   export_config: Dict[str, Any], 
                                   execution_result: Dict[str, Any]):
        """Store coordination history for tracking and debugging"""
        history_entry = {
            'coordination_id': coordination_id,
            'timestamp': self._get_timestamp(),
            'export_config': export_config,
            'execution_result': execution_result,
            'success': execution_result['success']
        }
        
        self.coordination_history.append(history_entry)
        
        # Keep only last 100 entries
        if len(self.coordination_history) > 100:
            self.coordination_history = self.coordination_history[-100:]
    
    def get_coordination_history(self, limit: int = 10) -> Dict[str, Any]:
        """Get coordination history"""
        return {
            'history': self.coordination_history[-limit:],
            'total_coordinations': len(self.coordination_history),
            'success_rate': self._calculate_success_rate(),
            'timestamp': self._get_timestamp()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate of coordinations"""
        if not self.coordination_history:
            return 0.0
        
        successful = sum(1 for entry in self.coordination_history if entry['success'])
        return successful / len(self.coordination_history)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all registered services"""
        service_status = {}
        
        for service_name, service_config in self.service_registry.items():
            health_status = self._check_service_health(service_config)
            service_status[service_name] = {
                'url': service_config['url'],
                'healthy': health_status['healthy'],
                'response_time': health_status.get('response_time'),
                'capabilities': service_config['capabilities']
            }
        
        return {
            'services': service_status,
            'total_services': len(self.service_registry),
            'healthy_services': sum(1 for s in service_status.values() if s['healthy']),
            'timestamp': self._get_timestamp()
        }
    
    def _generate_coordination_id(self) -> str:
        """Generate unique coordination ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()