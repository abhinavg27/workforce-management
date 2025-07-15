import google.generativeai as genai
import json
import logging
from datetime import datetime
import os
import re
import html

logger = logging.getLogger(__name__)

class UniversalLLMGenerator:
    def __init__(self, api_key, model_name="gemini-2.5-flash"):
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            self.enabled = True
            logger.info("🌟 Universal LLM Generator initialized - Enhanced Storage Format")
        else:
            self.model = None
            self.enabled = False
            logger.warning("Universal LLM not configured - API key missing")

    def generate_confluence_page(self, template_data, operation_date, display_date, operation_type,execution_steps=None):
        """🤖 Enhanced generator with proper Confluence storage format"""
        if not self.enabled:
            raise Exception("Universal LLM not configured")


        execution_steps = execution_steps or []

        # Dynamic space configuration based on operation type
        space_config = self._get_space_config(operation_type)

        # Format operation date
        formatted_date = f"{operation_date[:4]}-{operation_date[4:6]}-{operation_date[6:8]}" if operation_date and len(operation_date) >= 8 else "2025-06-20"
        operation_direction = self._get_operation_direction(operation_type)

        logger.info(f"🌟 Universal LLM generating {operation_type.upper()} page for space {space_config['space_key']}...")

        start_time = datetime.now()
        logger.info(f"🌟 Starting generate_confluence_page: operation_type={operation_type}, template_data={template_data},start_time={start_time}")
        try:
            # 🤖 Step 1: LLM analyzes template and creates content structure
            content_structure = self._llm_analyze_template(
                template_data, operation_type, operation_date, display_date,
                operation_direction, formatted_date
            )

            if execution_steps:
                for section in content_structure['sections']:
                    if section['heading'] == "Process Steps":
                        section['tables'][0]['rows'] = [{"cells": [step, "DONE"]} for step in execution_steps]
                        break
                else:
                    content_structure['sections'].append({
                        "heading": "Process Steps",
                        "tables": [
                            {
                                "headers": ["Step", "Status"],
                                "rows": [{"cells": [step, "DONE"]} for step in execution_steps]
                            }
                        ]
                    })

            # 🐍 Step 2: Build proper Confluence storage format
            content = self._build_confluence_storage_format(content_structure, operation_date, display_date, operation_direction, formatted_date)

            # Generate title
            title = self._generate_title(template_data, operation_type, operation_date)

            logger.info(f"🌟 Universal LLM generated content for {space_config['space_key']} space, length: {len(content)} characters")

            return title, content, space_config['space_key'], space_config['parent_page_id']

        except Exception as e:
            logger.error(f"🌟 Universal LLM generation failed: {e}")
            return self._universal_fallback(template_data, operation_date, display_date, operation_type)

    def _get_space_config(self, operation_type):
        """Get space configuration based on operation type - FIXED"""

        logger.info(f"🏠 Determining space for operation_type: '{operation_type}'")

        # Normalize operation type
        op_type_lower = operation_type.lower() if operation_type else ""

        # SCG Space: locker_in, locker_out
        if 'locker' in op_type_lower or operation_type in ['locker_in', 'locker_out']:
            config = {
                'space_key': os.getenv("CONFLUENCE_SCG_SPACE_KEY", "SCG"),
                'parent_page_id': os.getenv("CONFLUENCE_SCG_PARENT_PAGE_ID", "5880757738"),
                'space_name': "SCG (Shipping Carrier Gateway)"
            }
            logger.info(f"🏠 ✅ Using SCG space for {operation_type}: {config['space_key']}")
            return config

        # SCP Space: s_in, s_out
        elif operation_type in ['s_in', 's_out'] or 's_' in op_type_lower:
            config = {
                'space_key': os.getenv("CONFLUENCE_SCP_SPACE_KEY", "SCP"),
                'parent_page_id': os.getenv("CONFLUENCE_SCP_PARENT_PAGE_ID", "5890230619"),
                'space_name': "SCP (Shipping Calculation Platform)"
            }
            logger.info(f"🏠 ✅ Using SCP space for {operation_type}: {config['space_key']}")
            return config

        # Default fallback
        else:
            config = {
                'space_key': os.getenv("CONFLUENCE_DEFAULT_SPACE_KEY", "GENERAL"),
                'parent_page_id': os.getenv("CONFLUENCE_DEFAULT_PARENT_PAGE_ID", ""),
                'space_name': "General Operations"
            }
            logger.warning(f"🏠 ⚠️ Using default space for unknown operation {operation_type}: {config['space_key']}")
            return config

    def _get_operation_direction(self, operation_type):
        """Get operation direction from operation type"""
        if operation_type and 'out' in operation_type.lower():
            return "OUT"
        elif operation_type and 'in' in operation_type.lower():
            return "IN"
        else:
            return "UNKNOWN"

    def _build_confluence_storage_format(self, content_structure, operation_date, display_date, operation_direction, formatted_date):
        """🐍 Build proper Confluence storage format with macros"""

        html_parts = ['<div>']

        sections = content_structure.get('sections', [])

        for section in sections:
            # Add section header with proper styling
            heading = html.escape(str(section.get('heading', '')))
            html_parts.append(f'''<div style="background: linear-gradient(90deg, #be2422 0%, #d93e2d 100%); color: #fff; padding: 8px 16px; font-weight: bold; border-radius: 4px; margin-bottom: 24px; font-size: 24px;">
<h1>{heading}</h1>
</div>''')

            # Add tables with enhanced content processing
            tables = section.get('tables', [])
            for table in tables:
                html_parts.append(self._build_enhanced_table(table, operation_date, display_date, operation_direction, formatted_date))

        html_parts.append('</div>')

        return '\n'.join(html_parts)

    def _build_enhanced_table(self, table_data, operation_date, display_date, operation_direction, formatted_date):
        """Build table with proper Confluence macros and formatting"""

        table_parts = []

        # Table opening
        table_parts.append('<table style="border-collapse: collapse; width: 100%; background: #fff; border: 1px solid #003366; font-size: 15px;">')

        # Headers
        headers = table_data.get('headers', [])
        if headers:
            table_parts.append('<tr>')
            for header in headers:
                safe_header = html.escape(str(header))
                table_parts.append(f'<th style="border: 1px solid #ddd; background: #f7f7f7; vertical-align: top; font-weight: bold; padding: 8px;">{safe_header}</th>')
            table_parts.append('</tr>')

        # Rows with enhanced content processing
        rows = table_data.get('rows', [])
        for row in rows:
            table_parts.append('<tr>')
            cells = row.get('cells', [])
            for cell in cells:
                processed_content = self._process_enhanced_cell_content(str(cell), operation_date, display_date, operation_direction, formatted_date)
                table_parts.append(f'<td style="border: 1px solid #ddd; background: #fff; vertical-align: top; padding: 8px; color: #000; font-weight: normal;">{processed_content}</td>')
            table_parts.append('</tr>')

        # Table closing
        table_parts.append('</table>')

        return '\n'.join(table_parts)

    def _process_enhanced_cell_content(self, content, operation_date, display_date, operation_direction, formatted_date):
        """Simplified content processing to restore working functionality"""

        if not content or content == 'None':
            return ''

        # Replace variables first
        if operation_date:
            content = content.replace('{operation_date}', operation_date)
            content = content.replace('{{operation_date}}', operation_date)
        if display_date:
            content = content.replace('{display_date}', display_date)
            content = content.replace('{{display_date}}', display_date)

        # 🔧 SIMPLIFIED: Process in order to avoid conflicts

        # 1. Process expand macros first (before any HTML escaping)
        content = self._process_expand_macros_simple(content)

        # 2. Process code blocks
        content = self._process_code_blocks_simple(content)

        # 3. Process status labels
        content = self._process_status_labels_simple(content)

        # 4. Process URLs
        content = self._process_urls_simple(content)

        # 5. Handle line breaks
        content = content.replace('\\n', '<br/>')
        content = content.replace('\n', '<br/>')

        return content

    def _process_expand_macros_simple(self, content):
        """Simple expand macro processing"""

        # Pattern: {expand:title=Something}content{expand}
        pattern = r'\{expand:title=([^}]+)\}(.*?)\{expand\}'

        def replace_expand(match):
            title = match.group(1)
            body = match.group(2)

            return f'''<ac:structured-macro ac:name="expand">
<ac:parameter ac:name="title">{html.escape(title)}</ac:parameter>
<ac:rich-text-body>{body}</ac:rich-text-body>
</ac:structured-macro>'''

        return re.sub(pattern, replace_expand, content, flags=re.DOTALL)

    def _process_code_blocks_simple(self, content):
        """Simple code block processing"""

        # Pattern: {code:language=json|theme=RDark}content{code}
        pattern = r'\{code:([^}]*)\}(.*?)\{code\}'

        def replace_code(match):
            params = match.group(1)
            code_content = match.group(2).strip()

            # Extract language
            language = "text"
            if "language=" in params:
                lang_match = re.search(r'language=([^|]+)', params)
                if lang_match:
                    language = lang_match.group(1)

            return f'''<ac:structured-macro ac:name="code">
<ac:parameter ac:name="language">{language}</ac:parameter>
<ac:plain-text-body><![CDATA[{code_content}]]></ac:plain-text-body>
</ac:structured-macro>'''

        return re.sub(pattern, replace_code, content, flags=re.DOTALL)

    def _process_status_labels_simple(self, content):
        """Simple status label processing"""

        status_mappings = {
            'NOT APPROVED': '<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Red</ac:parameter><ac:parameter ac:name="title">NOT APPROVED</ac:parameter></ac:structured-macro>',
            'APPROVED': '<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Green</ac:parameter><ac:parameter ac:name="title">APPROVED</ac:parameter></ac:structured-macro>',
            'DONE': '<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Green</ac:parameter><ac:parameter ac:name="title">DONE</ac:parameter></ac:structured-macro>',
            'SKIP': '<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Grey</ac:parameter><ac:parameter ac:name="title">SKIP</ac:parameter></ac:structured-macro>',
            'NOT YET': '<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Red</ac:parameter><ac:parameter ac:name="title">NOT YET</ac:parameter></ac:structured-macro>',
            'NOT APPLICABLE': '<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Yellow</ac:parameter><ac:parameter ac:name="title">NOT APPLICABLE</ac:parameter></ac:structured-macro>'
        }

        for status_text, status_macro in status_mappings.items():
            content = content.replace(status_text, status_macro)

        return content

    def _process_urls_simple(self, content):
        """Simple URL processing"""

        # Pattern for URLs
        url_pattern = r'(https?://[^\s<>"{}|\\^`\[\]]+)'

        def replace_url(match):
            url = match.group(1)
            return f'<a href="{html.escape(url)}" target="_blank">{html.escape(url)}</a>'

        return re.sub(url_pattern, replace_url, content)

    def _llm_analyze_template(self, template_data, operation_type, operation_date, display_date, operation_direction, formatted_date):
        """🤖 LLM analyzes template and returns structured content"""

        prompt = f"""Analyze this JSON template and return ONLY a JSON structure with content mapping. Process ALL special formatting.

OPERATION: {operation_type.upper()} | DATE: {operation_date} | DIRECTION: {operation_direction}

TEMPLATE:
{json.dumps(template_data, indent=1) if template_data else '{}'}

TASK: Return JSON with this structure, preserving ALL special formatting:
{{
  "sections": [
    {{
      "heading": "Section Name",
      "tables": [
        {{
          "headers": ["Column1", "Column2", "Column3"],
          "rows": [
            {{
              "cells": ["Cell1 Content", "Cell2 Content", "Cell3 Content"]
            }}
          ]
        }}
      ]
    }}
  ]
}}

CONTENT PROCESSING RULES:
1. Map static_values to table cells using row IDs and suffixes (_steps, _remarks, _status)
2. Replace {{{{operation_date}}}} with {operation_date}
3. Replace {{{{display_date}}}} with {display_date}
4. PRESERVE all {{expand:title=...}}...{{expand}} blocks exactly as they are
5. PRESERVE all {{code:language=...}}...{{code}} blocks exactly as they are
6. PRESERVE all URLs starting with https:// exactly as they are
7. For status fields, use exact text like "NOT APPROVED", "DONE", "SKIP"
8. Keep ALL special formatting: expand blocks, code blocks, URLs
9. Process ALL sections from template
10. Map content intelligently based on field names and row IDs

CRITICAL: Do NOT convert expand/code blocks to HTML - keep them as {{expand}} and {{code}} syntax!

Return ONLY the JSON structure:"""

        try:
            response = self.model.generate_content(prompt)
            content_text = response.text.strip()

            # Clean up response to get valid JSON
            content_text = self._clean_llm_json_response(content_text)

            # Parse JSON
            content_structure = json.loads(content_text)
            logger.info("🤖 LLM successfully analyzed template structure with special formatting")
            return content_structure

        except Exception as e:
            logger.error(f"🤖 LLM template analysis failed: {e}")
            # Fallback to basic structure
            return self._create_basic_structure(template_data, operation_date, display_date)

    def _clean_llm_json_response(self, response_text):
        """Clean LLM response to extract valid JSON"""
        # Remove markdown code blocks
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith('```'):
                lines = lines[:-1]
            response_text = '\n'.join(lines)

        # Remove any text before first {
        start_idx = response_text.find('{')
        if start_idx > 0:
            response_text = response_text[start_idx:]

        # Remove any text after last }
        end_idx = response_text.rfind('}')
        if end_idx > 0:
            response_text = response_text[:end_idx + 1]

        return response_text.strip()

    def _create_basic_structure(self, template_data, operation_date, display_date):
        """Create basic structure when LLM fails"""
        logger.info("🐍 Creating basic structure fallback")

        sections = []

        if isinstance(template_data, dict) and 'sections' in template_data:
            for section in template_data['sections']:
                section_data = {
                    "heading": section.get('heading', 'Unknown Section'),
                    "tables": [
                        {
                            "headers": ["Field", "Value"],
                            "rows": [
                                {
                                    "cells": ["Operation Date", display_date or "Not specified"]
                                },
                                {
                                    "cells": ["Operation", operation_date or "Not specified"]
                                }
                            ]
                        }
                    ]
                }
                sections.append(section_data)
        else:
            # Create a default section
            sections = [{
                "heading": "Operation Details",
                "tables": [
                    {
                        "headers": ["Field", "Value"],
                        "rows": [
                            {"cells": ["Operation Date", display_date or "Not specified"]},
                            {"cells": ["Operation", operation_date or "Not specified"]}
                        ]
                    }
                ]
            }]

        return {"sections": sections}

    def _generate_title(self, template_data, operation_type, operation_date):
        """Generate unique title from template with GUARANTEED uniqueness"""

        title = None

        # Try to get title from template
        if isinstance(template_data, dict) and 'title' in template_data:
            title = template_data['title']
            logger.info(f"🏷️ Using template title: {title}")
        elif isinstance(template_data, list) and len(template_data) > 0:
            first_section = template_data[0]
            if isinstance(first_section, dict):
                title = first_section.get('title') or first_section.get('heading') or first_section.get('name')
                logger.info(f"🏷️ Extracted title from first section: {title}")

        # Fallback title generation
        if not title:
            title = f"{operation_type.upper()}_{operation_date}" if operation_type and operation_date else "Generated_Page"
            logger.info(f"🏷️ Generated fallback title: {title}")

        # Replace variables in title
        if operation_date:
            title = title.replace("{operation_date}", operation_date)
            title = title.replace("{{{operation_date}}}", operation_date)
            title = title.replace("{{operation_date}}", operation_date)

        # 🔧 FORCE UNIQUENESS: Always add timestamp and random component
        timestamp = datetime.now().strftime("%H%M%S")
        import random
        random_suffix = random.randint(100, 999)

        # Ensure title is not just "SCP" or similar
        if len(title.strip()) <= 5 or title.strip().upper() in ['SCP', 'SCG', 'GENERAL']:
            title = f"{operation_type.upper()}_Operation_{operation_date}_{timestamp}_{random_suffix}"
        else:
            title = f"{title}_{timestamp}_{random_suffix}"

        logger.info(f"🏷️ Final GUARANTEED unique title: {title}")
        return title

    def _universal_fallback(self, template_data, operation_date, display_date, operation_type):
        """Universal fallback with proper Confluence format"""
        logger.warning("🌟 Universal LLM using enhanced fallback...")

        space_config = self._get_space_config(operation_type)
        title = self._generate_title(template_data, operation_type, operation_date)

        formatted_date = f"{operation_date[:4]}-{operation_date[4:6]}-{operation_date[6:8]}" if operation_date and len(operation_date) >= 8 else "2025-06-20"

        content = f'''<div>
<div style="background: linear-gradient(90deg, #be2422 0%, #d93e2d 100%); color: #fff; padding: 8px 16px; font-weight: bold; border-radius: 4px; margin-bottom: 24px; font-size: 24px;">
<h1>Enhanced Fallback - {space_config['space_name']}</h1>
</div>
<table style="border-collapse: collapse; width: 100%; background: #fff; border: 1px solid #003366; font-size: 15px;">
<tr>
<th style="border: 1px solid #ddd; background: #f7f7f7; vertical-align: top; font-weight: bold; padding: 8px;">Field</th>
<th style="border: 1px solid #ddd; background: #f7f7f7; vertical-align: top; font-weight: bold; padding: 8px;">Value</th>
</tr>
<tr>
<td style="border: 1px solid #ddd; background: #fff; vertical-align: top; padding: 8px; color: #000; font-weight: normal;">Operation</td>
<td style="border: 1px solid #ddd; background: #fff; vertical-align: top; padding: 8px; color: #000; font-weight: normal;">{html.escape(operation_type.upper() if operation_type else 'UNKNOWN')}</td>
</tr>
<tr>
<td style="border: 1px solid #ddd; background: #fff; vertical-align: top; padding: 8px; color: #000; font-weight: normal;">Date</td>
<td style="border: 1px solid #ddd; background: #fff; vertical-align: top; padding: 8px; color: #000; font-weight: normal;"><time datetime="{formatted_date}" class="date-past">{html.escape(display_date if display_date else 'Not specified')}</time></td>
</tr>
<tr>
<td style="border: 1px solid #ddd; background: #fff; vertical-align: top; padding: 8px; color: #000; font-weight: normal;">Space</td>
<td style="border: 1px solid #ddd; background: #fff; vertical-align: top; padding: 8px; color: #000; font-weight: normal;">{html.escape(space_config['space_key'])}</td>
</tr>
<tr>
<td style="border: 1px solid #ddd; background: #fff; vertical-align: top; padding: 8px; color: #000; font-weight: normal;">Status</td>
<td style="border: 1px solid #ddd; background: #fff; vertical-align: top; padding: 8px; color: #000; font-weight: normal;"><ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Red</ac:parameter><ac:parameter ac:name="title">NOT APPROVED</ac:parameter></ac:structured-macro></td>
</tr>
</table>
</div>'''

        return title, content, space_config['space_key'], space_config['parent_page_id']