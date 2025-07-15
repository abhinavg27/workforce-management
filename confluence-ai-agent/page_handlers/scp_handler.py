import json
import os
from datetime import datetime
import re
import logging
from html import escape
import google.generativeai as genai
from dotenv import load_dotenv
from utils.gitUtils import ensure_repository
from utils.commonUtils import process_text_with_urls

# Load .env
load_dotenv(os.getenv("DOTENV_PATH", ".env"))
# Load environment variables from .env file
load_dotenv()

# Access environment variables
CONFLUENCE_SCP_SPACE_KEY = os.getenv("CONFLUENCE_SCP_SPACE_KEY", "SCP")
CONFLUENCE_SCG_SPACE_KEY = os.getenv("CONFLUENCE_SCG_SPACE_KEY", "SCG")
CONFLUENCE_SCP_PARENT_PAGE_ID = os.getenv("CONFLUENCE_SCP_PARENT_PAGE_ID", "5885681081")
CONFLUENCE_SCG_PARENT_PAGE_ID = os.getenv("CONFLUENCE_SCG_PARENT_PAGE_ID", "5880757738")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Validate MODEL_API_KEY
if not os.getenv("MODEL_API_KEY"):
    logger.error("Missing required environment variable: MODEL_API_KEY")
    raise ValueError("Missing required environment variable: MODEL_API_KEY")

# Constants
#GIT_REPO_PATH = ensure_repository()
TEMPLATE_DIR = "page_templates"
DEFAULT_TEMPLATE = "Please select the template"
DEFAULT_TABLE_STYLE = "border-collapse: collapse; width: 100%; border: 1px solid #ddd;"
DEFAULT_TH_STYLE = "border: 1px solid #ddd; padding: 8px; text-align: left;"
DEFAULT_TD_STYLE = "border: 1px solid #ddd; padding: 8px; text-align: left;"
HEADING_STYLE = "background: linear-gradient(90deg, #be2422 0%, #d93e2d 100%); color: #fff; padding: 8px 16px; font-weight: bold; border-radius: 4px; margin-bottom: 24px; font-size: 24px;"

# Set up the Gemini API key
MODEL_API_KEY = os.environ.get("MODEL_API_KEY")
if not MODEL_API_KEY:
    logger.error("MODEL_API_KEY environment variable not set.")
else:
    genai.configure(api_key=MODEL_API_KEY)
    model = genai.GenerativeModel('GEMINI_MODEL')

def load_template(template_name):
    """Load and validate a JSON template file."""
    file_path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.exists(file_path):
        logger.error(f"Error: File {file_path} does not exist.")
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data or not isinstance(data, dict):
                logger.error(f"Error: File {file_path} is empty or invalid.")
                return None
            logger.debug(f"Loaded file from {file_path}:")
            logger.debug(json.dumps(data, indent=2))
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
        return None

def sanitize_input(value):
    """Sanitize input to prevent XSS."""
    if isinstance(value, dict):
        return escape(json.dumps(value))
    return escape(str(value)) if value is not None else ""

def determine_space_with_llm(template_name, operation_type, form_data=None, llm_prompt=None):
    """Use Gemini LLM to determine the appropriate Confluence space."""
    if not MODEL_API_KEY:
        logger.warning("MODEL_API_KEY not set, falling back to default space")
        return CONFLUENCE_SCP_SPACE_KEY, False

    try:
        # Prepare context for the LLM
        context = f"Template name: {template_name}\nOperation type: {operation_type}"
        if form_data:
            context += f"\nForm data: {json.dumps(form_data, indent=2)}"
        if llm_prompt:
            context += f"\nUser prompt: {llm_prompt}"

        prompt = (
            f"Given the following context:\n{context}\n\n"
            f"You need to select a Confluence space for creating a page. The available spaces are:\n"
            f"- {CONFLUENCE_SCP_SPACE_KEY} (for SCP-related operations like s_in, s_out)\n"
            f"- {CONFLUENCE_SCG_SPACE_KEY} (for SCG-related operations like locker_out)\n\n"
            f"Based on the context, determine the appropriate space key. "
            f"Return ONLY the space key (e.g., '{CONFLUENCE_SCP_SPACE_KEY}' or '{CONFLUENCE_SCG_SPACE_KEY}'). "
            f"If you cannot determine the space, return '{CONFLUENCE_SCP_SPACE_KEY}' as the default."
        )
        logger.info(f"Calling Gemini LLM for space selection with prompt: {prompt[:200]}...")
        response = model.generate_content(prompt)
        space_key = response.text.strip()

        # Validate the LLM response
        if space_key not in [CONFLUENCE_SCP_SPACE_KEY, CONFLUENCE_SCG_SPACE_KEY]:
            logger.warning(f"LLM returned invalid space key: {space_key}. Falling back to default.")
            return CONFLUENCE_SCP_SPACE_KEY, True

        logger.debug(f"LLM selected space: {space_key}")
        return space_key, True

    except Exception as e:
        logger.error(f"Error using LLM to determine space: {e}", exc_info=True)
        return CONFLUENCE_SCP_SPACE_KEY, False
def render_expandable_code_block(content, operation_date, field_id):
    """Render Confluence expandable code blocks with preceding text."""
    html_output = ""
    try:
        content = content.replace("{operation_date}", operation_date)
        logger.debug(f"Processing static value for {field_id}: {content[:200]}...")

        # Split content into parts: text before macros and macro blocks
        macro_pattern = r'(\{expand:title=.*?}\s*\{code:.*?}.*?\{code\})'
        parts = re.split(macro_pattern, content, flags=re.DOTALL)

        for part in parts:
            if part.startswith("{expand:title="):
                # Process macro block
                title_match = re.search(r'\{expand:title=(.*?)\}', part)
                expand_title = title_match.group(1) if title_match else "Untitled"

                # More flexible code block regex
                code_match = re.search(
                    r'\{code:language=(.*?)(?:\|borderStyle=(.*?))?(?:\|theme=(.*?))?(?:\|collapse=(.*?))?\}\s*(.*?)\s*\{code\}',
                    part, re.DOTALL
                )
                if code_match:
                    groups = code_match.groups()
                    language = groups[0] or "none"
                    border_style = groups[1] or "solid"
                    theme = groups[2] or "Default"
                    collapse = groups[3] or "true"
                    code_content = groups[4] or ""

                    html_output += (
                        f'<ac:structured-macro ac:name="expand">'
                        f'<ac:parameter ac:name="title">{sanitize_input(expand_title)}</ac:parameter>'
                        f'<ac:rich-text-body>'
                        f'<ac:structured-macro ac:name="code">'
                        f'<ac:parameter ac:name="language">{sanitize_input(language)}</ac:parameter>'
                        f'<ac:parameter ac:name="borderStyle">{sanitize_input(border_style)}</ac:parameter>'
                        f'<ac:parameter ac:name="theme">{sanitize_input(theme)}</ac:parameter>'
                        f'<ac:parameter ac:name="collapse">{sanitize_input(collapse)}</ac:parameter>'
                        f'<ac:plain-text-body><![CDATA[{sanitize_input(code_content)}]]></ac:plain-text-body>'
                        f'</ac:structured-macro>'
                        f'</ac:rich-text-body>'
                        f'</ac:structured-macro>'
                    )
                else:
                    logger.warning(f"Invalid code block in {field_id}: {part[:100]}...")
                    html_output += f'<p>Invalid code block: {sanitize_input(part)}</p>'
            else:
                # Process plain text (e.g., "Login to SWAN")
                if part.strip():
                    part = sanitize_input(part).replace("\n", "<br/>")
                    part = re.sub(
                        r'(https?://(?:confluence\.rakuten-it\.com|kibana-eaas-jpe2c\.rakuten-it\.com|monitor\.rakuten\.com|gitpub\.rakuten-it\.com|api\.rakuten\.com|aspfjob201z\.prod\.jp\.localdomain:[0-9]+)/(?:[^\s/]+/)*[^\s/]+)',
                        r'<a href="\1">\1</a>',
                        part
                    )
                    html_output += f'<p>{part}</p>'

        return html_output
    except Exception as e:
        logger.error(f"Error in render_expandable_code_block for {field_id}: {e}", exc_info=True)
        return f'<p>Error rendering content for {field_id}: {sanitize_input(str(e))}</p>'


def render_task_list(values, field_id):
    """Render Confluence task list."""
    html_output = '<ac:task-list>'
    for value in values:
        task_id = f"task_{field_id}_{value['id']}"
        html_output += (
            f'<ac:task>'
            f'<ac:task-id>{sanitize_input(task_id)}</ac:task-id>'
            f'<ac:task-status>incomplete</ac:task-status>'
            f'<ac:task-body>{sanitize_input(value["text"])}</ac:task-body>'
            f'</ac:task>'
        )
    html_output += '</ac:task-list>'
    return html_output

def generate_llm_section1(section_name, prompt, operation_type, display_date):
    """Generate section content using LLM with robust fallback."""
    if not MODEL_API_KEY or not prompt:
        logger.warning(f"LLM not called for {section_name} due to missing API key or prompt")
        return (
            f'<table style="{DEFAULT_TABLE_STYLE}"><tr><th style="{DEFAULT_TH_STYLE}">Field</th><th style="{DEFAULT_TD_STYLE}">Value</th></tr>'
            f'<tr><td style="{DEFAULT_TD_STYLE}">{section_name}</td><td style="{DEFAULT_TD_STYLE}">LLM unavailable. Using template.</td></tr></table>',
            False
        )
    try:
        full_prompt = (
            f"Generate a Confluence-compatible HTML table for a '{section_name}' section for a {operation_type} operation "
            f"on {display_date}. The table MUST have two columns: 'Field' and 'Value'. Include exactly 3 fields: "
            f"1. Operation Type: {operation_type}, 2. Date: {display_date}, 3. Status: Planned. "
            f"Use style='{DEFAULT_TABLE_STYLE}' for the table, '{DEFAULT_TH_STYLE}' for headers, and '{DEFAULT_TD_STYLE}' for cells. "
            f"Return ONLY the HTML table code, starting with <table> and ending with </table>. "
            f"Example: <table style=\"{DEFAULT_TABLE_STYLE}\"><tr><th style=\"{DEFAULT_TH_STYLE}\">Field</th><th style=\"{DEFAULT_TH_STYLE}\">Value</th></tr>"
            f"<tr><td style=\"{DEFAULT_TD_STYLE}\">Operation Type</td><td style=\"{DEFAULT_TD_STYLE}\">{operation_type}</td></tr>...</table>"
        )
        logger.info(f"Calling Gemini LLM for {section_name} with prompt: {full_prompt[:200]}...")
        response = model.generate_content(full_prompt)
        llm_output = sanitize_input(response.text)
        logger.info(f"Raw LLM output for {section_name}: {llm_output[:500]}...")

        if "<table" not in llm_output:
            logger.warning(f"LLM output for {section_name} does not contain a table: {llm_output[:200]}...")
            lines = llm_output.strip().split("\n")
            table_rows = ""
            for line in lines[:3]:
                if ":" in line:
                    field, value = line.split(":", 1)
                    table_rows += (
                        f'<tr><td style="{DEFAULT_TD_STYLE}">{sanitize_input(field.strip())}</td>'
                        f'<td style="{DEFAULT_TD_STYLE}">{sanitize_input(value.strip())}</td></tr>'
                    )
                elif line.startswith("- ") or line.startswith("* "):
                    parts = line[2:].split(": ", 1)
                    if len(parts) == 2:
                        field, value = parts
                        table_rows += (
                            f'<tr><td style="{DEFAULT_TD_STYLE}">{sanitize_input(field.strip())}</td>'
                            f'<td style="{DEFAULT_TD_STYLE}">{sanitize_input(value.strip())}</td></tr>'
                        )
            if table_rows:
                llm_output = (
                    f'<table style="{DEFAULT_TABLE_STYLE}">'
                    f'<tr><th style="{DEFAULT_TH_STYLE}">Field</th><th style="{DEFAULT_TH_STYLE}">Value</th></tr>'
                    f'{table_rows}</table>'
                )
            else:
                table_rows = (
                    f'<tr><td style="{DEFAULT_TD_STYLE}">Operation Type</td><td style="{DEFAULT_TD_STYLE}">{operation_type}</td></tr>'
                    f'<tr><td style="{DEFAULT_TD_STYLE}">Date</td><td style="{DEFAULT_TD_STYLE}">{display_date}</td></tr>'
                    f'<tr><td style="{DEFAULT_TD_STYLE}">Status</td><td style="{DEFAULT_TD_STYLE}">Planned</td></tr>'
                )
                llm_output = (
                    f'<table style="{DEFAULT_TABLE_STYLE}">'
                    f'<tr><th style="{DEFAULT_TH_STYLE}">Field</th><th style="{DEFAULT_TH_STYLE}">Value</th></tr>'
                    f'{table_rows}</table>'
                )
                logger.warning(f"Used predefined fallback for {section_name}")
                return llm_output, True

        return llm_output, True
    except Exception as e:
        logger.error(f"Error generating LLM content for {section_name}: {e}", exc_info=True)
        table_rows = (
            f'<tr><td style="{DEFAULT_TD_STYLE}">Operation Type</td><td style="{DEFAULT_TD_STYLE}">{operation_type}</td></tr>'
            f'<tr><td style="{DEFAULT_TD_STYLE}">Date</td><td style="{DEFAULT_TD_STYLE}">{display_date}</td></tr>'
            f'<tr><td style="{DEFAULT_TD_STYLE}">Status</td><td style="{DEFAULT_TD_STYLE}">Planned</td></tr>'
        )
        llm_output = (
            f'<table style="{DEFAULT_TABLE_STYLE}">'
            f'<tr><th style="{DEFAULT_TH_STYLE}">Field</th><th style="{DEFAULT_TH_STYLE}">Value</th></tr>'
            f'{table_rows}</table>'
        )
        return llm_output, False

def generate_llm_section(section_name, prompt, operation_type, display_date):
    """Generate section content using LLM with fallback."""
    if not MODEL_API_KEY or not prompt:
        return (
            f'<table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd;"><tr><th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Field</th><th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Value</th></tr>'
            f'<tr><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">{section_name}</td><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">LLM unavailable.</td></tr></table>',
            False
        )
    try:
        full_prompt = (
            f"Generate a Confluence-compatible HTML table for a '{section_name}' section for a {operation_type} operation "
            f"on {display_date}. The table MUST have two columns: 'Field' and 'Value'. Include exactly 3 fields: "
            f"1. Operation Type: {operation_type}, 2. Date: {display_date}, 3. Status: Planned. "
            f"Use style='border-collapse: collapse; width: 100%; border: 1px solid #ddd;' for the table, "
            f"'border: 1px solid #ddd; padding: 8px; text-align: left;' for headers and cells. "
            f"Return ONLY the HTML table code, starting with <table> and ending with </table>. "
        )
        genai.configure(api_key=MODEL_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(full_prompt)
        llm_output = sanitize_input(response.text)
        if "<table" not in llm_output:
            table_rows = (
                f'<tr><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">Operation Type</td><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">{operation_type}</td></tr>'
                f'<tr><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">Date</td><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">{display_date}</td></tr>'
                f'<tr><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">Status</td><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">Planned</td></tr>'
            )
            llm_output = (
                f'<table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd;">'
                f'<tr><th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Field</th><th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Value</th></tr>'
                f'{table_rows}'
                f'</table>'
            )
        return llm_output, True
    except Exception as e:
        logger.error(f"Error generating LLM content for {section_name}: {e}", exc_info=True)
        table_rows = (
            f'<tr><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">Operation Type</td><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">{operation_type}</td></tr>'
            f'<tr><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">Date</td><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">{display_date}</td></tr>'
            f'<tr><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">Status</td><td style="border: 1px solid #ddd; padding: 8px; text-align: left;">Planned</td></tr>'
        )
        llm_output = (
            f'<table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd;">'
            f'<tr><th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Field</th><th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Value</th></tr>'
            f'{table_rows}'
            f'</table>'
        )
        return llm_output, False

def generate_content(form_data=None, llm_prompt=None, template_name=DEFAULT_TEMPLATE):
    """Generate HTML content based on a JSON template."""
    llm_called = False
    try:
        template = load_template(template_name)
        if not template:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fallback_title = f"SCP_vShop_ingestion_{timestamp}"
            return fallback_title, "<div><p>Template not found or invalid.</p></div>", llm_called,CONFLUENCE_SCP_SPACE_KEY, CONFLUENCE_SCP_PARENT_PAGE_ID

        form_data = form_data or {}
        operation_date = form_data.get("operation_date", datetime.now().strftime("%Y%m%d"))
        display_date = form_data.get("display_date", datetime.now().strftime("%d %B %Y"))
        operation_type = form_data.get("operation_type", template_name.split('.')[0].upper())
        title = template.get("title", f"SCP_vShop_ingestion_{operation_date}")
        title = title.replace("{operation_date}", operation_date)
        timestamp = datetime.now().strftime("%H%M%S")
        title = f"{title}_{timestamp}"
        title = re.sub(r'[^\x20-\x7E]', '', title)
        logger.debug(f"Generated title: {title}")

        # Determine Confluence space using LLM
        space_key, space_llm_called = determine_space_with_llm(template_name, operation_type, form_data, llm_prompt)
        llm_called = llm_called or space_llm_called

        # Determine parent page ID based on selected space (keeping existing logic for now)
        if space_key == CONFLUENCE_SCG_SPACE_KEY:
            parent_page_id = CONFLUENCE_SCG_PARENT_PAGE_ID
        else:
            parent_page_id = CONFLUENCE_SCP_PARENT_PAGE_ID
        logger.debug(f"Using space_key: {space_key}, parent_page_id: {parent_page_id} for template: {template_name}")


        def get_field_value(field_id, static_values, default_value="",for_attribute=False):
            """Retrieve and sanitize field value, prioritizing static_values with default."""
            value = static_values.get(field_id, form_data.get(field_id, default_value))
            logger.debug(f"Field {field_id}: static_value={static_values.get(field_id)}, form_data={form_data.get(field_id)}, default={default_value}, final={value}")
            # Handle status macro format {status:LABEL}
            status_match = re.match(r'\{status:(.*?)\}', str(value))
            if status_match:
                label = sanitize_input(status_match.group(1))
                return f'<p><span class="status-macro aui-lozenge conf-macro output-inline" data-hasbody="false" data-macro-name="status">{label}</span></p>'
                #return sanitize_input(value.replace("{operation_date}", operation_date))

            # Sanitize the value and replace operation_date
            final_value = sanitize_input(str(value).replace("{operation_date}", operation_date))

            # Only process URLs if the value is not intended for an attribute
            if not for_attribute:
                final_value = process_text_with_urls(final_value)
            return final_value

        html_content = "<div>"

        for section_index, section in enumerate(template.get("sections", [])):
            heading = sanitize_input(section.get("heading", "Unnamed Section"))
            html_content += f'<div style="{HEADING_STYLE}"><h1>{heading}</h1></div>'

            for content_index, content_element in enumerate(section.get("content", [])):
                if content_element.get("type") != "table":
                    html_content += f"<p>Content type '{sanitize_input(content_element.get('type', 'unknown'))}' not implemented.</p>"
                    continue

                table_style = content_element.get("style", DEFAULT_TABLE_STYLE)
                html_content += f'<table style="{table_style}">'

                html_content += "<tr>"
                for field in content_element.get("fields", []):
                    th_style = field.get("style", DEFAULT_TH_STYLE)
                    label = sanitize_input(field.get("label", ""))
                    html_content += f'<th style="{th_style}">{label}</th>'
                html_content += "</tr>"

                static_values = content_element.get("static_values", {})
                rows = content_element.get("rows", [])

                # Operation Overview section
                if section_index == 0 and content_index == 0:
                    for row in rows:
                        html_content += "<tr>"
                        label = sanitize_input(row.get("label", ""))
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">{label}</td>'
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">'
                        field_id = row.get("id", "")

                        if field_id == "display_date":
                            html_content += display_date
                        elif field_id == "ticket":
                            html_content += get_field_value("ticket", static_values)
                        elif field_id == "approvals_sre":
                            approvers = get_field_value("approvals_sre", static_values,for_attribute=True)
                            email_map = static_values.get("approvals_sre_emails", {})
                            approver_list = [a.strip() for a in approvers.split() if a.strip()]
                            linked_approvers = []
                            for approver in approver_list:
                                email = email_map.get(approver, "")
                                if email:
                                    linked_approvers.append(f'<a href="mailto:{sanitize_input(email)}">{sanitize_input(approver)}</a>')
                                else:
                                    linked_approvers.append(sanitize_input(approver))
                            html_content += " ".join(linked_approvers)
                        elif field_id == "operation_pic":
                            html_content += get_field_value("operation_pic", static_values)
                        elif field_id == "operation_buddy":
                            html_content += get_field_value("operation_buddy", static_values)
                        elif field_id == "other_attendees":
                            html_content += get_field_value("other_attendees", static_values)
                        elif field_id == "operation_details":
                            html_content += get_field_value("operation_details", static_values, "Operation details")
                        elif field_id == "operation_summary":
                            if MODEL_API_KEY and llm_prompt:
                                logger.info(f"Calling Gemini LLM for operation_summary with prompt: {llm_prompt}")
                                llm_content, called = generate_llm_section("Operation Summary", llm_prompt, operation_type, display_date)
                                html_content += llm_content
                                llm_called = llm_called or called
                            else:
                                html_content += get_field_value("operation_summary", static_values, "Operation summary")
                        elif field_id == "release_branch_checkboxes":
                            for option in row.get("checkboxes", []):
                                task_id = f"task_{field_id}_{option.lower().replace(' ', '_')}"
                                html_content += f'<ac:task-list><ac:task><ac:task-id>{task_id}</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>{option}</ac:task-body></ac:task></ac:task-list>'
                        elif field_id == "release_branch_name":
                            html_content += get_field_value("release_branch_name", static_values)
                        else:
                            html_content += get_field_value(field_id, static_values)

                        html_content += '</td>'

                        if len(content_element.get("fields", [])) > 2:
                            status_value = get_field_value(f"{field_id}_status", static_values)
                            if field_id == "approvals_sre":
                                status_value = get_field_value("approvals_sre_status", static_values)
                            elif field_id == "release_branch_checkboxes":
                                status_value = get_field_value("release_branch_checkboxes_status", static_values)
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{status_value}</td>'
                        html_content += "</tr>"

                # Locker/S-IN/S-OUT Preparation or Operation Manual
                elif section_index == 1 and content_index == 0:
                    for row in rows:
                        html_content += "<tr>"
                        label = sanitize_input(row.get("label", ""))
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">{label}</td>'
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">'
                        field_id = row.get("id", "")

                        if field_id in ["verify_shop_exists", "check_main_warehouse_center_cd", "check_id_with_center_name", "verify_locker_presence_db", "verify_locker_status", "review_comments", "locker_master_data_change"]:
                            html_content += render_expandable_code_block(get_field_value(field_id, static_values), operation_date, field_id)
                        elif field_id == "check_center_name_for_code":
                            center_codes = static_values.get("center_codes_data", [])
                            if not center_codes:
                                html_content += "No center codes available."
                            else:
                                html_content += '<table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd;">'
                                html_content += '<tr><th style="border: 1px solid #ddd; background: #f7f7f7; font-weight: bold;">Code</th><th style="border: 1px solid #ddd; background: #f7f7f7; font-weight: bold;">Name</th><th style="border: 1px solid #ddd; background: #f7f7f7; font-weight: bold;">Alias</th></tr>'
                                for center in center_codes:
                                    code = sanitize_input(center.get("code", ""))
                                    name = sanitize_input(center.get("name", ""))
                                    alias = sanitize_input(center.get("alias", ""))
                                    html_content += f'<tr><td style="border: 1px solid #ddd;">{code}</td><td style="border: 1px solid #ddd;">{name}</td><td style="border: 1px solid #ddd;">{alias}</td></tr>'
                                html_content += '</table>'
                        else:
                            html_content += get_field_value(field_id, static_values)

                        html_content += '</td>'
                        if len(content_element.get("fields", [])) > 2:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(f"{field_id}_screenshots", static_values) or get_field_value(f"{field_id}_remarks", static_values, "")}</td>'
                        if len(content_element.get("fields", [])) > 3:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(f"{field_id}_stg_review", static_values)}</td>'
                        if len(content_element.get("fields", [])) > 4:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(f"{field_id}_prod_review", static_values)}</td>'
                        html_content += "</tr>"

                # Locker/S-IN/S-OUT Execution or Operation Steps
                elif section_index == 2 and content_index == 0:
                    for row in rows:
                        html_content += "<tr>"
                        label = sanitize_input(row.get("label", "")).replace("\n", "<br/>")
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">{label}</td>'
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">'
                        field_id = row.get("id", "")

                        if field_id in ["verify_shop_warehouse_location_data", "update_shop_data_out", "execute_s_out", "locker_master_data_change"]:
                            html_content += render_expandable_code_block(get_field_value(field_id, static_values), operation_date, field_id)
                        elif field_id in ["import_shop_warehouse_location_data", "update_shop_data", "update_shop_warehouse_location_data"]:
                            static_value = get_field_value(field_id, static_values)
                            static_value = static_value.replace("\n", "<br/>")
                            html_content += static_value
                        else:
                            html_content += get_field_value(field_id, static_values)

                        html_content += '</td>'
                        if len(content_element.get("fields", [])) > 2:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(f"{field_id}_remarks", static_values, "")}</td>'
                        if len(content_element.get("fields", [])) > 3:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(f"{field_id}_stg_review", static_values)}</td>'
                        if len(content_element.get("fields", [])) > 4:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(f"{field_id}_prod_review", static_values)}</td>'
                        html_content += "</tr>"

                # Locker/S-IN/S-OUT Verification or Rollback
                elif section_index in [3, 4] and content_index == 0:
                    for row in rows:
                        html_content += "<tr>"
                        label = sanitize_input(row.get("label", ""))
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">{label}</td>'
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">'
                        field_id = row.get("id", "")

                        if field_id in [
                            "verify_seller_code_warehouse_shop_url", "verify_items_published",
                            "verify_sample_items_scp_calculation", "query_after_sin_zero_quantity",
                            "connect_target_server", "connect_to_db", "insert_locker_master",
                            "insert_vacant_locker", "restore_locker_vacant", "locker_master_data_change"
                        ]:
                            html_content += render_expandable_code_block(get_field_value(field_id, static_values), operation_date, field_id)
                        elif field_id == "vacant_locker_api":
                            static_value = get_field_value(field_id, static_values)
                            static_value = static_value.replace("\n", "<br/>")
                            html_content += static_value
                        else:
                            html_content += get_field_value(field_id, static_values)

                        html_content += '</td>'
                        if len(content_element.get("fields", [])) > 2:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(f"{field_id}_remarks", static_values, "")}</td>'
                        if len(content_element.get("fields", [])) > 3:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(f"{field_id}_stg_review", static_values)}</td>'
                        if len(content_element.get("fields", [])) > 4:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(f"{field_id}_prod_review", static_values)}</td>'
                        html_content += "</tr>"

                # Monitoring Plan
                elif section_index == 5 and content_index == 0:
                    for row in rows:
                        html_content += "<tr>"
                        label = sanitize_input(row.get("label", ""))
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">{label}</td>'
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">'
                        field_id = row.get("id", "")

                        if field_id == "monitor_kibana":
                            static_value = get_field_value(field_id, static_values)
                            static_value = static_value.replace("\n", "<br/>")
                            html_content += static_value
                        else:
                            html_content += get_field_value(field_id, static_values)

                        html_content += '</td>'
                        if len(content_element.get("fields", [])) > 2:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value("monitoring_pic", static_values)}</td>'
                        if len(content_element.get("fields", [])) > 3:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value("monitoring_time", static_values)}</td>'
                        html_content += "</tr>"

                # Post Release Checklist
                elif section_index == 6 and content_index == 0:
                    for row in rows:
                        html_content += "<tr>"
                        label = sanitize_input(row.get("label", ""))
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">{label}</td>'
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">'
                        field_id = row.get("id", "")

                        if field_id == "request_branch_merge":
                            for option in row.get("checkboxes", []):
                                task_id = f"task_{field_id}_{option.lower().replace(' ', '_')}"
                                html_content += f'<ac:task-list><ac:task><ac:task-id>{task_id}</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>{option}</ac:task-body></ac:task></ac:task-list>'
                        else:
                            html_content += get_field_value(field_id, static_values)

                        html_content += '</td>'
                        if len(content_element.get("fields", [])) > 2:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(f"{field_id}_remarks", static_values)}</td>'
                        html_content += "</tr>"

                else:
                    for row in rows:
                        html_content += "<tr>"
                        label = sanitize_input(row.get("label", ""))
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">{label}</td>'
                        field_id = row.get("id", "")
                        html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(field_id, static_values)}</td>'
                        if len(content_element.get("fields", [])) > 2:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(f"{field_id}_extra", static_values)}</td>'
                        if len(content_element.get("fields", [])) > 3:
                            html_content += f'<td style="{DEFAULT_TD_STYLE}">{get_field_value(f"{field_id}_extra2", static_values)}</td>'
                        html_content += "</tr>"

                html_content += "</table>"

        html_content += "</div>"

        if not html_content.strip():
            logger.error("Generated HTML content is empty.")
            return title, "<div><p>Error: Generated content is empty.</p></div>", llm_called

        return title, html_content, llm_called, space_key, parent_page_id

    except Exception as e:
        logger.error(f"Error generating content: {e}", exc_info=True)
        return "Error", f"<div><p>An unexpected error occurred: {str(e)}</p></div>", llm_called

def generate_content1(form_data=None, llm_prompt=None, template_name=DEFAULT_TEMPLATE):
    """Generate Confluence storage format content based on a JSON template."""
    llm_called = False
    try:
        template = load_template(template_name)
        if not template:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"Error_{timestamp}", "<div><p>Template not found or invalid.</p></div>", llm_called

        form_data = form_data or {}
        properties = template.get("properties", {})
        operation_date = form_data.get("operation_date", datetime.now().strftime(properties.get("operation_date", "%Y%m%d")))
        display_date = form_data.get("display_date", datetime.now().strftime(properties.get("display_date", "%d %B %Y")))
        operation_type = form_data.get("operation_type", template_name.split('.')[0].upper())
        title = template.get("title", f"SCP_{operation_type}_{operation_date}").replace("{operation_date}", operation_date)
        timestamp = datetime.now().strftime("%H%M%S")
        title = f"{title}_{timestamp}"
        title = re.sub(r'[^\x20-\x7E]', '', title)

        def get_field_value(field_id, static_values, default_value=""):
            value = static_values.get(field_id, form_data.get(field_id, default_value))
            status_match = re.match(r'\{status:(.*?)\}', str(value))
            if status_match:
                label = sanitize_input(status_match.group(1))
                return f'<span class="status-macro aui-lozenge">{label}</span>'
            if field_id in ["verify_locker_presence_db", "locker_master_data_change", "execute_s_in", "execute_s_out"]:
                return render_expandable_code_block(str(value), operation_date, field_id)
            value = str(value).replace("{operation_date}", operation_date)
            value = re.sub(
                r'(https?://(?:confluence\.rakuten-it\.com|kibana-eaas-jpe2c\.rakuten-it\.com|monitor\.rakuten\.com|gitpub\.rakuten-it\.com|api\.rakuten\.com|aspfjob201z\.prod\.jp\.localdomain:[0-9]+)/(?:[^\s/]+/)*[^\s/]+)',
                r'<a href="\1">\1</a>',
                value
            )
            return sanitize_input(value)

        html_content = '<div xmlns:ac="http://atlassian.com">'
        for section_index, section in enumerate(template.get("sections", [])):
            heading = sanitize_input(section.get("heading", "Unnamed Section"))
            heading_id = f"id-[{operation_type}]{operation_date[:4]}/{operation_date[4:6]}/{operation_date[6:8]}Operation-{heading.replace(' ', '')}"
            html_content += f'<div style="{HEADING_STYLE}"><h1 id="{heading_id}">{heading}</h1></div>'

            if template_name == "locker_out.json" and heading == "Operation Manual":
                operation_date_formatted = f"{operation_date[:4]}/{operation_date[4:6]}/{operation_date[6:8]}"
                html_content += (
                    f'<h3 id="id-[LockerPickup]{operation_date_formatted}Operation-OperationPreparation">Operation Preparation</h3>'
                    f'<h3 id="id-[LockerPickup]{operation_date_formatted}Operation-OperationSteps">Operation Steps</h3>'
                    f'<h3 id="id-[LockerPickup]{operation_date_formatted}Operation-Verification">Verification</h3>'
                )

            for content_element in section.get("content", []):
                content_type = content_element.get("type", "")
                if content_type == "task-list":
                    values = content_element.get("values", [])
                    field_id = content_element.get("id", "task_list")
                    html_content += render_task_list(values, field_id)
                    continue
                if content_type != "table":
                    html_content += f"<p>Content type '{sanitize_input(content_type)}' not implemented.</p>"
                    continue

                table_style = content_element.get("style", "border-collapse: collapse; width: 100%; border: 1px solid #ddd;")
                html_content += f'<table style="{table_style}">'
                fields = content_element.get("fields", [{"label": "Field"}, {"label": "Value"}])
                html_content += "<tr>"
                for field in fields:
                    field_style = field.get("style", "border: 1px solid #ddd; padding: 8px; text-align: left;")
                    html_content += f'<th style="{field_style}">{sanitize_input(field.get("label", ""))}</th>'
                html_content += "</tr>"

                static_values = content_element.get("static_values", {})
                rows = content_element.get("rows", [])

                for row in rows:
                    html_content += "<tr>"
                    row_label = sanitize_input(row.get("label", ""))
                    row_id = row.get("id", "")
                    field_values = [
                        get_field_value(row_id, static_values),
                        get_field_value(f"{row_id}_stg_review", static_values, "{status:SKIP}"),
                        get_field_value(f"{row_id}_prod_review", static_values, "{status:NOT YET}")
                    ]

                    for i, field in enumerate(fields):
                        field_id = field.get("id", "")
                        field_style = field.get("style", "border: 1px solid #ddd; padding: 8px; text-align: left;")
                        if field_id == "field_label" or field_id in ["preparation_task", "execution_task", "rollback_step"]:
                            html_content += f'<td style="{field_style}">{row_label}</td>'
                        elif field_id == "field_status" or field_id in ["stg_review", "prod_review"]:
                            if i < len(field_values) and field_values[i]:
                                html_content += f'<td style="{field_style}">{field_values[i]}</td>'
                            else:
                                html_content += f'<td style="{field_style}"></td>'
                        else:
                            if i < len(field_values):
                                html_content += f'<td style="{field_style}">{field_values[i]}</td>'
                            else:
                                html_content += f'<td style="{field_style}"></td>'

                    html_content += "</tr>"

                html_content += "</table>"

        html_content += "</div>"
        logger.debug(f"Generated HTML content: {html_content[:500]}...")
        return title, html_content, llm_called
    except Exception as e:
        logger.error(f"Error generating content: {e}", exc_info=True)
        return "Error", f"<div><p>An unexpected error occurred: {sanitize_input(str(e))}</p></div>", llm_called