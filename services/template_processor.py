"""
Template Processor Service
Processes content using publication templates
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class TemplateProcessor:
    """Service for processing content with publication templates"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.formatting_rules = self._initialize_formatting_rules()
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize publication templates"""
        return {
            'article': {
                'name': 'Research Article',
                'sections': [
                    'title', 'authors', 'abstract', 'keywords',
                    'introduction', 'methodology', 'results',
                    'discussion', 'conclusion', 'references'
                ],
                'required_sections': ['title', 'authors', 'abstract'],
                'section_order': True,
                'max_abstract_words': 250,
                'reference_format': 'numeric'
            },
            'conference_paper': {
                'name': 'Conference Paper',
                'sections': [
                    'title', 'authors', 'abstract', 'keywords',
                    'introduction', 'approach', 'experiments',
                    'results', 'conclusion', 'references'
                ],
                'required_sections': ['title', 'authors', 'abstract'],
                'section_order': True,
                'max_abstract_words': 150,
                'reference_format': 'numeric'
            },
            'technical_report': {
                'name': 'Technical Report',
                'sections': [
                    'title', 'authors', 'executive_summary',
                    'introduction', 'background', 'analysis',
                    'findings', 'recommendations', 'appendices'
                ],
                'required_sections': ['title', 'authors', 'executive_summary'],
                'section_order': False,
                'max_abstract_words': 500,
                'reference_format': 'author_year'
            },
            'thesis': {
                'name': 'Thesis/Dissertation',
                'sections': [
                    'title_page', 'abstract', 'acknowledgments',
                    'table_of_contents', 'introduction', 'literature_review',
                    'methodology', 'results', 'discussion',
                    'conclusion', 'references', 'appendices'
                ],
                'required_sections': ['title_page', 'abstract', 'introduction'],
                'section_order': True,
                'max_abstract_words': 350,
                'reference_format': 'author_year'
            }
        }
    
    def _initialize_formatting_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize formatting rules for different elements"""
        return {
            'text_formatting': {
                'emphasis': {
                    'italic': r'\*([^*]+)\*',
                    'bold': r'\*\*([^*]+)\*\*',
                    'underline': r'_([^_]+)_'
                },
                'special_characters': {
                    'degree': '°',
                    'plus_minus': '±',
                    'micro': 'μ',
                    'alpha': 'α',
                    'beta': 'β',
                    'gamma': 'γ'
                }
            },
            'citations': {
                'numeric': r'\[(\d+(?:,\s*\d+)*)\]',
                'author_year': r'\(([A-Za-z]+(?:\s+et\s+al\.)?),?\s+(\d{4})\)',
                'inline': r'([A-Za-z]+(?:\s+et\s+al\.)?)\s+\((\d{4})\)'
            },
            'equations': {
                'inline': r'\$([^$]+)\$',
                'display': r'\$\$([^$]+)\$\$',
                'numbered': r'\\begin\{equation\}(.*?)\\end\{equation\}'
            },
            'figures_tables': {
                'figure_ref': r'Figure\s+(\d+)',
                'table_ref': r'Table\s+(\d+)',
                'equation_ref': r'Equation\s+(\d+)'
            }
        }
    
    def process_content(self, content: str, style_name: str, 
                       template_type: str = 'article') -> Dict[str, Any]:
        """
        Process content with specified publication style and template
        
        Args:
            content: Content to process
            style_name: Publication style to apply
            template_type: Type of template to use
            
        Returns:
            Dictionary containing processed content and metadata
        """
        if template_type not in self.templates:
            raise ValueError(f"Unsupported template type: {template_type}")
        
        template_config = self.templates[template_type]
        
        # Parse content into sections
        sections = self._parse_content_sections(content)
        
        # Validate required sections
        validation_result = self._validate_sections(sections, template_config)
        
        # Apply formatting rules
        formatted_sections = self._apply_formatting(sections, style_name)
        
        # Generate table of contents if needed
        toc = self._generate_table_of_contents(formatted_sections, template_config)
        
        # Process citations and references
        citation_info = self._process_citations(formatted_sections, style_name)
        
        # Calculate statistics
        statistics = self._calculate_content_statistics(formatted_sections)
        
        return {
            'template_type': template_type,
            'style_name': style_name,
            'sections': formatted_sections,
            'table_of_contents': toc,
            'citations': citation_info,
            'validation': validation_result,
            'statistics': statistics,
            'metadata': {
                'timestamp': self._get_timestamp(),
                'processing_id': self._generate_processing_id(),
                'template_config': template_config
            }
        }
    
    def _parse_content_sections(self, content: str) -> Dict[str, str]:
        """Parse content into sections based on headers"""
        sections = {}
        current_section = 'introduction'
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check for section headers
            if line.startswith('#'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                header_text = line.lstrip('#').strip().lower()
                current_section = self._normalize_section_name(header_text)
                current_content = []
            else:
                if line:  # Skip empty lines at section boundaries
                    current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _normalize_section_name(self, header_text: str) -> str:
        """Normalize section name to match template expectations"""
        normalization_map = {
            'abstract': 'abstract',
            'introduction': 'introduction',
            'background': 'background',
            'literature review': 'literature_review',
            'methodology': 'methodology',
            'methods': 'methodology',
            'approach': 'approach',
            'experiments': 'experiments',
            'experimental setup': 'experiments',
            'results': 'results',
            'findings': 'findings',
            'discussion': 'discussion',
            'analysis': 'analysis',
            'conclusion': 'conclusion',
            'conclusions': 'conclusion',
            'references': 'references',
            'bibliography': 'references',
            'acknowledgments': 'acknowledgments',
            'acknowledgements': 'acknowledgments',
            'appendix': 'appendices',
            'appendices': 'appendices'
        }
        
        return normalization_map.get(header_text, header_text.replace(' ', '_'))
    
    def _validate_sections(self, sections: Dict[str, str], 
                          template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate sections against template requirements"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_required': [],
            'unexpected_sections': []
        }
        
        required_sections = template_config.get('required_sections', [])
        allowed_sections = template_config.get('sections', [])
        
        # Check required sections
        for required in required_sections:
            if required not in sections:
                validation_result['missing_required'].append(required)
                validation_result['errors'].append(f'Missing required section: {required}')
                validation_result['valid'] = False
        
        # Check for unexpected sections
        for section in sections:
            if section not in allowed_sections:
                validation_result['unexpected_sections'].append(section)
                validation_result['warnings'].append(f'Unexpected section: {section}')
        
        # Check abstract word count
        if 'abstract' in sections and 'max_abstract_words' in template_config:
            abstract_words = len(sections['abstract'].split())
            max_words = template_config['max_abstract_words']
            if abstract_words > max_words:
                validation_result['warnings'].append(
                    f'Abstract exceeds maximum word count: {abstract_words}/{max_words}'
                )
        
        return validation_result
    
    def _apply_formatting(self, sections: Dict[str, str], 
                         style_name: str) -> Dict[str, Dict[str, Any]]:
        """Apply formatting rules to sections"""
        formatted_sections = {}
        
        for section_name, content in sections.items():
            formatted_content = content
            
            # Apply text formatting
            formatted_content = self._apply_text_formatting(formatted_content)
            
            # Process citations
            citations = self._extract_citations(formatted_content)
            
            # Process equations
            equations = self._extract_equations(formatted_content)
            
            # Process figures and tables references
            references = self._extract_references(formatted_content)
            
            formatted_sections[section_name] = {
                'content': formatted_content,
                'word_count': len(formatted_content.split()),
                'citations': citations,
                'equations': equations,
                'references': references,
                'formatting_applied': True
            }
        
        return formatted_sections
    
    def _apply_text_formatting(self, content: str) -> str:
        """Apply text formatting rules"""
        # Convert markdown-style formatting
        content = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', content)  # Bold
        content = re.sub(r'\*([^*]+)\*', r'*\1*', content)        # Italic
        content = re.sub(r'_([^_]+)_', r'_\1_', content)          # Underline
        
        return content
    
    def _extract_citations(self, content: str) -> List[Dict[str, Any]]:
        """Extract citation information from content"""
        citations = []
        
        # Numeric citations [1], [2,3]
        numeric_matches = re.finditer(self.formatting_rules['citations']['numeric'], content)
        for match in numeric_matches:
            citations.append({
                'type': 'numeric',
                'text': match.group(0),
                'numbers': [int(n.strip()) for n in match.group(1).split(',')],
                'position': match.span()
            })
        
        # Author-year citations
        author_year_matches = re.finditer(self.formatting_rules['citations']['author_year'], content)
        for match in author_year_matches:
            citations.append({
                'type': 'author_year',
                'text': match.group(0),
                'author': match.group(1),
                'year': int(match.group(2)),
                'position': match.span()
            })
        
        return citations
    
    def _extract_equations(self, content: str) -> List[Dict[str, Any]]:
        """Extract equation information from content"""
        equations = []
        
        # Inline equations $...$
        inline_matches = re.finditer(self.formatting_rules['equations']['inline'], content)
        for i, match in enumerate(inline_matches):
            equations.append({
                'type': 'inline',
                'content': match.group(1),
                'position': match.span(),
                'id': f'eq_inline_{i+1}'
            })
        
        # Display equations $$...$$
        display_matches = re.finditer(self.formatting_rules['equations']['display'], content)
        for i, match in enumerate(display_matches):
            equations.append({
                'type': 'display',
                'content': match.group(1),
                'position': match.span(),
                'id': f'eq_display_{i+1}'
            })
        
        return equations
    
    def _extract_references(self, content: str) -> List[Dict[str, Any]]:
        """Extract figure/table/equation references"""
        references = []
        
        # Figure references
        fig_matches = re.finditer(self.formatting_rules['figures_tables']['figure_ref'], content)
        for match in fig_matches:
            references.append({
                'type': 'figure',
                'number': int(match.group(1)),
                'text': match.group(0),
                'position': match.span()
            })
        
        # Table references
        table_matches = re.finditer(self.formatting_rules['figures_tables']['table_ref'], content)
        for match in table_matches:
            references.append({
                'type': 'table',
                'number': int(match.group(1)),
                'text': match.group(0),
                'position': match.span()
            })
        
        return references
    
    def _generate_table_of_contents(self, sections: Dict[str, Dict[str, Any]], 
                                   template_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate table of contents"""
        toc = []
        section_order = template_config.get('sections', [])
        
        for i, section_name in enumerate(section_order):
            if section_name in sections:
                toc.append({
                    'section': section_name,
                    'title': section_name.replace('_', ' ').title(),
                    'page': i + 1,  # Placeholder page number
                    'word_count': sections[section_name]['word_count']
                })
        
        return toc
    
    def _process_citations(self, sections: Dict[str, Dict[str, Any]], 
                          style_name: str) -> Dict[str, Any]:
        """Process citations and generate bibliography"""
        all_citations = []
        
        for section_data in sections.values():
            all_citations.extend(section_data['citations'])
        
        # Remove duplicates and sort
        unique_citations = {}
        for citation in all_citations:
            if citation['type'] == 'numeric':
                for num in citation['numbers']:
                    unique_citations[num] = citation
            elif citation['type'] == 'author_year':
                key = f"{citation['author']}_{citation['year']}"
                unique_citations[key] = citation
        
        return {
            'total_citations': len(all_citations),
            'unique_citations': len(unique_citations),
            'citation_style': style_name,
            'citations': list(unique_citations.values())
        }
    
    def _calculate_content_statistics(self, sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate content statistics"""
        total_words = sum(section['word_count'] for section in sections.values())
        total_citations = sum(len(section['citations']) for section in sections.values())
        total_equations = sum(len(section['equations']) for section in sections.values())
        total_references = sum(len(section['references']) for section in sections.values())
        
        return {
            'total_words': total_words,
            'total_sections': len(sections),
            'total_citations': total_citations,
            'total_equations': total_equations,
            'total_references': total_references,
            'section_breakdown': {
                name: data['word_count'] for name, data in sections.items()
            }
        }
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get specific template configuration"""
        if template_name in self.templates:
            template = self.templates[template_name].copy()
            template['metadata'] = {
                'timestamp': self._get_timestamp(),
                'template_name': template_name
            }
            return template
        return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()
    
    def _generate_processing_id(self) -> str:
        """Generate unique processing ID"""
        import uuid
        return str(uuid.uuid4())