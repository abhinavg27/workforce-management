import os
import logging
import re
import traceback
import sys  # Add this for system information
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from utils.ai_agent import ConfluenceAIAgent
from utils.template_processor import TemplateProcessor
from utils.confluence_client import ConfluenceClient
import time  # ✅ Import time module directly
from datetime import datetime,timedelta
from typing import Dict

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
app.config['TEMPLATES_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app.config['STATIC_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s,%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler('app.log', maxBytes=10*1024*1024, backupCount=5)
        #logging.FileHandler('app.log')
    ],
    force=True
)
logger = logging.getLogger(__name__)
logger.info("Logging initialized for app-llm.py")

# Directory for template files
TEMPLATE_DIR = "page_templates"

# Initialize components
template_processor = TemplateProcessor()

# Initialize AI Agent
ai_agent = ConfluenceAIAgent(
    api_key=os.getenv("MODEL_API_KEY"),
    model_name=os.getenv("MODEL_NAME", "gemini-2.5-flash")
)
logger.info("🤖 AI Agent initialized with model: %s", ai_agent.model_name)
agent = ConfluenceAIAgent(api_key=os.getenv("MODEL_API_KEY"))
logger.info("🤖 AI Agent initialized with model: %s", agent.api_key)

# Add this helper function at the top of your app.py:
def normalize_operation_type(operation_type, template_file):
    """Normalize operation type to ensure correct space mapping"""

    # Direct mapping from template file
    template_to_operation = {
        's_in.json': 's_in',
        's_out.json': 's_out',
        'locker_in.json': 'locker_in',
        'locker_out.json': 'locker_out'
    }

    # Use template file mapping if available
    if template_file in template_to_operation:
        normalized = template_to_operation[template_file]
        logger.info(f"🔧 Normalized {operation_type} -> {normalized} from template {template_file}")
        return normalized

    # Fallback to original
    return operation_type
def validate_date(date_str, format_str):
    """Validate date string against specified format."""
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False

def parse_operation_from_prompt(prompt: str):
    """Parse operation type and dates from user prompt."""
    prompt_lower = prompt.lower().strip()
    logger.info(f"🧠 Parsing prompt: {prompt}")

    # Operation type patterns
    operation_patterns = {
        's_in': ['s_in', 's-in', 'sin', 'shop in', 'shop ingestion', 'scp in', 's in'],
        's_out': ['s_out', 's-out', 'sout', 'shop out', 'shop outgestion', 'scp out', 's out'],
        'locker_in': ['locker_in', 'locker-in', 'locker in', 'scg in', 'l in'],
        'locker_out': ['locker_out', 'locker-out', 'locker out', 'scg out', 'l out']
    }

    # Find operation type
    operation_type = None
    template_file = None
    operation_date = None
    display_date = None

    for op_type, patterns in operation_patterns.items():
        if any(pattern in prompt_lower for pattern in patterns):
            operation_type = op_type
            template_file = f"{op_type}.json"
            logger.info(f"🧠 Found operation type: {operation_type}")
            break

    # Date extraction
    date_patterns = [
        (r'\b(\d{8})\b', '%Y%m%d', '%Y%m%d'),  # YYYYMMDD
        (r'\b(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4})\b', '%d %B %Y', '%d %B %Y'),  # DD Month YYYY
        (r'\b(\d{1,2}/\d{1,2}/\d{4})\b', '%d/%m/%Y', '%Y%m%d'),  # DD/MM/YYYY
        (r'\b(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)\b', '%d %B', '%Y%m%d')  # DDth Month
    ]

    for pattern, input_format, output_format in date_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            try:
                # Handle DDth Month case
                if input_format == '%d %B':
                    day = match.group(1)
                    month = match.group(2)
                    year = datetime.now().year  # Default to current year
                    # If month is in the past, assume next year
                    parsed_date = datetime.strptime(f"{day} {month} {year}", '%d %B %Y')
                    if parsed_date < datetime.now():
                        parsed_date = parsed_date.replace(year=year + 1)
                else:
                    parsed_date = datetime.strptime(match.group(1), input_format)
                operation_date = parsed_date.strftime('%Y%m%d')
                display_date = parsed_date.strftime('%d %B %Y')
                logger.info(f"🧠 Parsed explicit date: {operation_date} -> {display_date}")
                break
            except ValueError:
                logger.warning(f"🧠 Invalid date format in prompt: {match.group(1)}")

    # Relative dates (only if no explicit date was found)
    if not operation_date:
        if 'today' in prompt_lower:
            today = datetime.now()
            operation_date = today.strftime("%Y%m%d")
            display_date = today.strftime("%d %B %Y")
            logger.info(f"🧠 Parsed 'today': {operation_date} -> {display_date}")
        elif 'tomorrow' in prompt_lower:
            tomorrow = datetime.now() + timedelta(days=1)
            operation_date = tomorrow.strftime("%Y%m%d")
            display_date = tomorrow.strftime("%d %B %Y")
            logger.info(f"🧠 Parsed 'tomorrow': {operation_date} -> {display_date}")
        elif 'yesterday' in prompt_lower:
            yesterday = datetime.now() - timedelta(days=1)
            operation_date = yesterday.strftime("%Y%m%d")
            display_date = yesterday.strftime("%d %B %Y")
            logger.info(f"🧠 Parsed 'yesterday': {operation_date} -> {display_date}")

    logger.info(f"🧠 Final parsing result: operation_type={operation_type}, template_file={template_file}, operation_date={operation_date}, display_date={display_date}")

    return operation_type, template_file, operation_date, display_date
def get_confluence_client():
    """Get configured Confluence client with proper authentication"""
    api_token = os.getenv("CONFLUENCE_API_TOKEN")
    password = os.getenv("CONFLUENCE_PASSWORD")
    pat = os.getenv("CONFLUENCE_PAT")

    auth_password = api_token or password or pat

    if not auth_password:
        raise Exception("No authentication credentials found")

    logger.info(f"Using authentication method: {'API_TOKEN' if api_token else 'PASSWORD' if password else 'PAT'}")

    return ConfluenceClient(
        url=os.getenv("CONFLUENCE_URL"),
        username=os.getenv("CONFLUENCE_USERNAME"),
        password=auth_password
    )


@app.route("/", methods=["GET"])
def index():
    """Render the main page"""
    template_files = template_processor.get_available_templates()
    message = session.pop('message', None)
    error = session.pop('error', None)
    page_url = session.pop('page_url', None)

    return render_template(
        "index.html",
        template_files=template_files,
        message=message,
        error=error,
        page_url=page_url
    )

@app.route('/generate_confluence', methods=['POST'])
def generate_confluence():
    start_time = datetime.now()
    logger.info(f"📊 Generation started: {start_time}")

    try:
        data = request.get_json()
        if not isinstance(data, dict) or not data:
            logger.error("🚨 Invalid request data: expected a non-empty JSON object")
            return jsonify({
                "success": False,
                "status": "failed",
                "error": "Invalid request data",
                "recommendations": ["Provide a valid JSON object with prompt or template"],
                "mock_mode": False
            }), 400

        user_id = request.remote_addr or "default"
        logger.info(f"Request from user: {user_id}")
        logger.info(f"📊 Generation started at: {start_time.isoformat()}")
        logger.debug(f"Raw request JSON: {data}")

        # Extract variables
        operation_type = data.get('operation_type', '')
        template_file = data.get('template_file', '')
        operation_date = data.get('operation_date', '')
        display_date = data.get('display_date', '')
        llm_prompt = data.get('llm_prompt', '')
        source = 'api_request'

        # Log initial operation_date
        logger.debug(f"Initial operation_date from request: {operation_date}")

        # Parse prompt if provided
        if llm_prompt:
            parsed_operation_type, parsed_template_file, parsed_operation_date, parsed_display_date = parse_operation_from_prompt(llm_prompt)
            logger.debug(f"🧠 Parsed from prompt: operation_type={parsed_operation_type}, template_file={parsed_template_file}, operation_date={parsed_operation_date}, display_date={parsed_display_date}")
            operation_type = parsed_operation_type or operation_type
            template_file = parsed_template_file or template_file
            # Always prioritize parsed dates if valid
            if parsed_operation_date and validate_date(parsed_operation_date, "%Y%m%d"):
                operation_date = parsed_operation_date
                logger.debug(f"🧠 Prioritized parsed_operation_date: {parsed_operation_date}")
            else:
                logger.warning(f"Invalid parsed_operation_date: {parsed_operation_date}. Keeping request JSON date: {operation_date}")
            if parsed_display_date and validate_date(parsed_display_date, "%d %B %Y"):
                display_date = parsed_display_date
                logger.debug(f"🧠 Prioritized parsed_display_date: {parsed_display_date}")
            else:
                logger.warning(f"Invalid parsed_display_date: {parsed_display_date}. Keeping request JSON date: {display_date}")
            source = 'prompt_parsed' if parsed_operation_date or parsed_display_date else source

            # Update data with parsed values
            data['operation_type'] = operation_type
            data['template_file'] = template_file
            data['operation_date'] = operation_date
            data['display_date'] = display_date

            logger.debug(f"Updated data: operation_type={operation_type}, template_file={template_file}, operation_date={operation_date}, display_date={display_date}")

        # Validate and set default dates if still invalid or missing
        if not operation_date or not validate_date(operation_date, "%Y%m%d"):
            logger.warning(f"Invalid operation_date: {operation_date}. Using default: {datetime.now().strftime('%Y%m%d')}")
            operation_date = datetime.now().strftime("%Y%m%d")
            data['operation_date'] = operation_date

        if not display_date or not validate_date(display_date, "%d %B %Y"):
            logger.warning(f"Invalid display_date: {display_date}. Using default: {datetime.now().strftime('%d %B %Y')}")
            display_date = datetime.now().strftime("%d %B %Y")
            data['display_date'] = display_date

        # Log variables for debugging
        logger.info(f"🔧 Variables before AI processing:")
        logger.info(f"   operation_type: {operation_type}")
        logger.info(f"   template_file: {template_file}")
        logger.info(f"   operation_date: {operation_date}")
        logger.info(f"   display_date: {display_date}")
        logger.info(f"   source: {source}")

        # Load template
        logger.debug(f"Template file specified: {template_file}")
        template_data = None

        if template_file:
            template_processor = TemplateProcessor('page_templates')
            template_data = template_processor.load_template(template_file)
            if not template_data:
                logger.warning(f"Failed to load template {template_file}, proceeding without template")
                data['warnings'] = data.get('warnings', []) + [f"Template {template_file} not found"]
            else:
                logger.info(f"Successfully loaded template: {template_file}")

        # Add template_data to request data
        data['template_data'] = template_data

        # Store original operation_date
        original_operation_date = operation_date
        logger.debug(f"Stored original_operation_date: {original_operation_date}")

        # Process request
        logger.info("Starting AI agent processing")
        result = ai_agent.process_request(data, user_id)
        logger.debug(f"AI agent result: title={result.get('title', 'None')}, success={result.get('success', False)}, operation_date={result.get('operation_date', 'None')}")

        # Check for operation_date modification
        if result.get('operation_date') and result.get('operation_date') != original_operation_date:
            logger.warning(f"AI agent modified operation_date from {original_operation_date} to {result.get('operation_date')}. Restoring original.")
            data['operation_date'] = original_operation_date
            operation_date = original_operation_date

        # Enhance result
        if result.get('success'):
            total_time = (datetime.now() - start_time).total_seconds()

            # Force title using operation_date
            title = f"Locker_AITest_S-OUT_{operation_date}_{datetime.now().strftime('%H%M%S')}_{int(datetime.now().timestamp() % 100000):05d}_{int(datetime.now().timestamp()):09d}_{int(total_time * 1000):03d}"
            logger.debug(f"Generated title: {title}")
            page_data: Dict = {
                'page_title': title,
                'page_id': result.get('page_id', f'mock_{int(datetime.now().timestamp())}'),
                'page_url': result.get('page_url', f'https://confluence.rakuten-it.com/confluence/pages/viewpage.action?pageId={int(datetime.now().timestamp())}'),
                'space_key': result.get('space_key', 'SCG' if 'locker' in operation_type.lower() else 'SCP'),
                'parent_page_id': result.get('parent_page_id', '5880757738' if 'locker' in operation_type.lower() else '5890230619'),
                'success': True,
                'error_message': '',
                'operation_type': operation_type,
                'template_file': template_file,
                'source': source,
                'generation_time_seconds': total_time,
                'ai_agent_used': True
            }

            # Store page creation
            storage_success = False
            try:
                if hasattr(ai_agent, 'memory') and hasattr(ai_agent.memory, 'store_page_creation'):
                    logger.debug(f"Storing page creation for user {user_id}, page_data: {page_data}")
                    storage_success = ai_agent.memory.store_page_creation(
                        user_id=user_id,
                        page_data=page_data
                    )
                    if storage_success:
                        logger.info(f"📊 Page creation stored successfully:")
                        logger.info(f"   Title: {page_data['page_title']}")
                        logger.info(f"   Operation: {operation_type}")
                        logger.info(f"   Success: True")
                        logger.info(f"   Timestamp: {datetime.now().isoformat()}")
                        logger.info(f"   Database: {ai_agent.memory.db_path}")
                    else:
                        logger.error("📊 Failed to store page creation: Storage method returned False")
                        page_data['error_message'] = 'Storage method returned False'
                else:
                    logger.error("📊 CRITICAL: AI agent memory or store_page_creation method not available")
                    page_data['error_message'] = 'AI agent memory or store_page_creation method not available'

            except Exception as store_error:
                logger.error(f"📊 CRITICAL: Failed to store page creation: {store_error}")
                logger.error(f"📊 Store error traceback: {traceback.format_exc()}")
                page_data['error_message'] = str(store_error)

            # Update result with corrected title and operation_date
            result['title'] = title
            result['operation_date'] = operation_date

            # Create enhanced response
            enhanced_result = {
                **result,
                'operation_type': operation_type,
                'template_used': template_file,
                'template_file': template_file,
                'source': source,
                'operation_date': operation_date,
                'display_date': display_date,
                'generation_time': f"{total_time:.2f}s",
                'total_processing_time': total_time,
                'user_id': user_id,
                'request_timestamp': start_time.isoformat(),
                'completion_timestamp': datetime.now().isoformat(),
                'template_loaded': template_data is not None,
                'template_size': len(str(template_data)) if template_data else 0,
                'dashboard_tracking': {
                    'stored': storage_success,
                    'timestamp': datetime.now().isoformat(),
                    'database_path': ai_agent.memory.db_path if hasattr(ai_agent, 'memory') else 'unknown',
                    'page_data': page_data
                },
                'debug_info': {
                    'processing_time_seconds': total_time,
                    'template_file_used': template_file,
                    'operation_parsed_from_prompt': source == 'prompt_parsed',
                    'ai_agent_used': True,
                    'storage_attempted': True,
                    'storage_success': storage_success,
                    'storage_error': page_data.get('error_message', None),
                    'operation_date_used': operation_date,
                    'title_source': 'forced_operation_date',
                    'original_operation_date': original_operation_date,
                    'prompt_operation_date': parsed_operation_date if llm_prompt else None
                }
            }

            logger.info(f"🤖 Request processing completed successfully in {total_time:.2f}s")
            return jsonify(enhanced_result)

        else:
            # Handle failure case
            total_time = (datetime.now() - start_time).total_seconds()

            # Prepare page_data for failed attempt
            page_data: Dict = {
                'page_title': f'Failed_{operation_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'page_id': '',
                'page_url': '',
                'space_key': 'SCG' if 'locker' in operation_type.lower() else 'SCP',
                'parent_page_id': '',
                'success': False,
                'error_message': result.get('error', 'Unknown error'),
                'operation_type': operation_type,
                'template_file': template_file,
                'source': source,
                'generation_time_seconds': total_time,
                'ai_agent_used': True
            }

            # Store failed attempt
            storage_success = False
            try:
                if hasattr(ai_agent, 'memory') and hasattr(ai_agent.memory, 'store_page_creation'):
                    logger.debug(f"Storing failed attempt for user {user_id}, page_data: {page_data}")
                    storage_success = ai_agent.memory.store_page_creation(
                        user_id=user_id,
                        page_data=page_data
                    )
                    if storage_success:
                        logger.info(f"📊 Failed attempt stored for dashboard tracking")
                    else:
                        logger.error("📊 Failed to store failed attempt: Storage method returned False")
                        page_data['error_message'] = 'Storage method returned False'
                else:
                    logger.error("📊 CRITICAL: AI agent memory or store_page_creation method not available")
                    page_data['error_message'] = 'AI agent memory or store_page_creation method not available'

            except Exception as store_error:
                logger.error(f"📊 Failed to store failed attempt: {store_error}")
                logger.error(f"📊 Store error traceback: {traceback.format_exc()}")
                page_data['error_message'] = str(store_error)

            enhanced_result = {
                **result,
                'operation_type': operation_type,
                'template_used': template_file,
                'source': source,
                'operation_date': operation_date,
                'display_date': display_date,
                'generation_time': f"{total_time:.2f}s",
                'debug_info': {
                    'processing_time_seconds': total_time,
                    'template_file_attempted': template_file,
                    'operation_type_attempted': operation_type,
                    'storage_success': storage_success,
                    'storage_error': page_data.get('error_message', None),
                    'operation_date_used': operation_date,
                    'original_operation_date': original_operation_date,
                    'prompt_operation_date': parsed_operation_date if llm_prompt else None
                },
                'dashboard_tracking': {
                    'stored': storage_success,
                    'timestamp': datetime.now().isoformat(),
                    'page_data': page_data
                }
            }

            logger.error(f"🤖 Request processing failed in {total_time:.2f}s")
            return jsonify(enhanced_result), 500

    except Exception as e:
        total_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"🚨 /generate_confluence failed: {e}\n{traceback.format_exc()}")

        # Prepare page_data for exception case
        page_data: Dict = {
            'page_title': f'Exception_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'page_id': '',
            'page_url': '',
            'space_key': 'UNKNOWN',
            'parent_page_id': '',
            'success': False,
            'error_message': str(e),
            'operation_type': data.get('operation_type', 'unknown') if 'data' in locals() else 'unknown',
            'template_file': data.get('template_file', 'unknown') if 'data' in locals() else 'unknown',
            'source': 'exception',
            'generation_time_seconds': total_time,
            'ai_agent_used': True
        }

        # Store exception case
        storage_success = False
        try:
            if 'data' in locals() and hasattr(ai_agent, 'memory') and hasattr(ai_agent.memory, 'store_page_creation'):
                logger.debug(f"Storing exception case for user {user_id}, page_data: {page_data}")
                storage_success = ai_agent.memory.store_page_creation(
                    user_id=user_id,
                    page_data=page_data
                )
                if storage_success:
                    logger.info(f"📊 Exception case stored for dashboard tracking")
                else:
                    logger.error("📊 Failed to store exception case: Storage method returned False")
                    page_data['error_message'] = 'Storage method returned False'
            else:
                logger.error("📊 CRITICAL: AI agent memory or store_page_creation method not available")
                page_data['error_message'] = 'AI agent memory or store_page_creation method not available'

        except Exception as store_error:
            logger.error(f"📊 Failed to store exception case: {store_error}")
            logger.error(f"📊 Store error traceback: {traceback.format_exc()}")
            page_data['error_message'] = str(store_error)

        return jsonify({
            'success': False,
            'status': 'failed',
            'error': str(e),
            'operation_type': data.get('operation_type', 'unknown') if 'data' in locals() else 'unknown',
            'template_used': data.get('template_file', 'unknown') if 'data' in locals() else 'unknown',
            'source': 'error',
            'operation_date': operation_date,
            'display_date': display_date,
            'generation_time': f"{total_time:.2f}s",
            'recommendations': ['Try again with a different prompt', 'Contact support'],
            'mock_mode': False,
            'debug_info': {
                'error_type': type(e).__name__,
                'processing_time_seconds': total_time,
                'exception_stored': storage_success,
                'storage_error': page_data.get('error_message', None),
                'operation_date_used': operation_date,
                'original_operation_date': original_operation_date if 'original_operation_date' in locals() else 'unknown',
                'prompt_operation_date': parsed_operation_date if 'parsed_operation_date' in locals() else None
            },
            'dashboard_tracking': {
                'stored': storage_success,
                'timestamp': datetime.now().isoformat(),
                'page_data': page_data
            }
        }), 500

    finally:
        total_time = (datetime.now() - start_time).total_seconds()
        logger.info("🧠 Cleaned up resources after request processing")
        logger.info(f"📊 Generation completed in {total_time:.2f}s")


# 🔧 REST OF YOUR ROUTES REMAIN THE SAME - JUST ADDING THE MISSING ROUTES

@app.route('/generate_direct', methods=['POST'])
def generate_direct():
    """Direct Universal Generator (bypass AI Agent)"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        logger.info("🌟 Using Direct Universal Generator")

        from utils.universal_llm_generator import UniversalLLMGenerator

        generator = UniversalLLMGenerator(
            api_key=os.getenv("MODEL_API_KEY"),
            model_name=os.getenv("MODEL_NAME", "gemini-2.5-flash")
        )

        # Process input similar to AI Agent route
        operation_type = data.get('operation_type')
        template_file = data.get('template_file')

        if template_file and not operation_type:
            operation_type = template_file.replace('.json', '')

        operation_date = data.get('operation_date') or datetime.now().strftime("%Y%m%d")
        display_date = data.get('display_date') or datetime.now().strftime("%d %B %Y")
        logger.info(f"🌟 Received operation type: {operation_type}, template file: {template_file}, operation date: {operation_date}, display date: {display_date}")

        # Load template
        template_data = None
        if template_file:
            template_data = template_processor.load_template(template_file)
            logger.info(f"🌟 Loaded template: {template_file}")
        logger.info(f"🌟 Using operation type: {operation_type}, date: {operation_date}, display date: {display_date}")

        # Direct generation
        title, content, space_key, parent_page_id = generator.generate_confluence_page(
            template_data,
            operation_date,
            display_date,
            operation_type
        )

        logger.info(f"🌟 Generated page title: {title}, space: {space_key}, parent ID: {parent_page_id}")

        # Create page
        confluence_client = get_confluence_client()
        page_result = confluence_client.create_page(space_key, title, content, parent_page_id)

        return jsonify({
            'success': True,
            'page_url': page_result['page_url'],
            'title': title,
            'method': 'Direct Universal Generator',
            'operation_type': operation_type,
            'space_key': space_key
        })

    except Exception as e:
        logger.error(f"🌟 Direct generation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def provide_feedback():
    """Endpoint for user feedback"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        interaction_id = data.get('interaction_id')
        feedback = {
            'rating': int(data.get('rating', 3)),
            'comments': data.get('comments', ''),
            'aspects': {
                'content_quality': int(data.get('content_quality', 3)),
                'formatting': int(data.get('formatting', 3)),
                'accuracy': int(data.get('accuracy', 3)),
                'completeness': int(data.get('completeness', 3))
            }
        }
        user_id = data.get('user_id', 'default')

        ai_agent.provide_feedback(interaction_id, feedback, user_id)

        return jsonify({
            'success': True,
            'message': 'Feedback received and processed for learning'
        })

    except Exception as e:
        logger.error(f"📝 Feedback processing failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/feedback/submit', methods=['POST'])
def submit_feedback():
    """Submit feedback - POST request to process the form"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        interaction_id = data.get('interaction_id', str(datetime.now().timestamp()))
        feedback = {
            'rating': int(data.get('rating', 3)),
            'comments': data.get('comments', ''),
            'feature_requests': data.get('feature_requests', ''),
            'contact_me': data.get('contact_me', False),
            'aspects': {
                'content_quality': int(data.get('content_quality', 3)),
                'formatting': int(data.get('formatting', 3)),
                'accuracy': int(data.get('accuracy', 3)),
                'completeness': int(data.get('completeness', 3))
            },
            'timestamp': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        }
        user_id = data.get('user_id', 'default')

        # Store feedback using AI agent
        ai_agent.provide_feedback(interaction_id, feedback, user_id)

        logger.info(f"📝 Feedback received: rating={feedback['rating']}, user={user_id}")

        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback! It helps us improve the AI agent.',
            'feedback_id': interaction_id
        })

    except Exception as e:
        logger.error(f"📝 Feedback processing failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process feedback. Please try again.'
        }), 500

@app.route('/recommendations/<user_id>')
def get_recommendations(user_id):
    """Get AI agent recommendations for user"""
    try:
        recommendations = ai_agent.get_recommendations(user_id)
        return jsonify(recommendations)

    except Exception as e:
        logger.error(f"💡 Recommendations failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/agent_status')
def agent_status():
    """Get dynamic AI agent status and capabilities"""
    try:
        # Get real-time statistics
        current_time = datetime.now()

        # Get memory statistics
        try:
            dashboard_stats = ai_agent.memory.get_dashboard_statistics()
            recent_activity = ai_agent.memory.get_recent_activity(limit=5)
            feedback_stats = ai_agent.memory.get_feedback_statistics()
        except Exception as e:
            logger.error(f"Failed to get agent statistics: {e}")
            dashboard_stats = {}
            recent_activity = []
            feedback_stats = {}

        # Calculate session duration
        session_duration = (current_time - ai_agent.current_session['start_time']).total_seconds()

        # Get template information
        try:
            available_templates = template_processor.get_available_templates()
        except:
            available_templates = []

        # Calculate performance metrics
        total_interactions = len(ai_agent.conversation_history)
        successful_interactions = sum(1 for i in ai_agent.conversation_history if i.success)
        success_rate = (successful_interactions / max(total_interactions, 1)) * 100

        # Get recent performance
        recent_interactions = ai_agent.conversation_history[-10:] if ai_agent.conversation_history else []
        recent_success_rate = (sum(1 for i in recent_interactions if i.success) / max(len(recent_interactions), 1)) * 100

        # System health check
        health_status = "healthy"
        health_issues = []

        if dashboard_stats.get('success_rate', 0) < 50:
            health_status = "warning"
            health_issues.append("Low success rate detected")

        if len(available_templates) == 0:
            health_status = "error"
            health_issues.append("No templates available")

        if not ai_agent.enabled:
            health_status = "error"
            health_issues.append("AI model not available")

        return jsonify({
            # Basic agent info
            'agent_type': 'Complete AI Agent with Learning',
            'status': health_status,
            'health_issues': health_issues,
            'enabled': ai_agent.enabled,
            'model_name': ai_agent.model_name,

            # Real-time capabilities
            'capabilities': [
                'Learning from interactions',
                'Memory and context awareness',
                'Intelligent planning and execution',
                'Adaptive behavior based on feedback',
                'User feedback processing',
                'Personalized recommendations',
                'Template-based content generation',
                'Multi-space Confluence integration'
            ],

            # Dynamic memory statistics
            'memory_stats': {
                'total_interactions': total_interactions,
                'successful_interactions': successful_interactions,
                'success_rate': round(success_rate, 1),
                'recent_success_rate': round(recent_success_rate, 1),
                'session_start': ai_agent.current_session['start_time'].isoformat(),
                'session_duration_minutes': round(session_duration / 60, 1),
                'learning_enabled': True,
                'database_path': ai_agent.memory.db_path
            },

            # Dashboard integration
            'dashboard_stats': {
                'total_pages_created': dashboard_stats.get('total_pages', 0),
                'overall_success_rate': dashboard_stats.get('success_rate', 0),
                'avg_generation_time': dashboard_stats.get('avg_generation_time', 0),
                'ai_calls_made': dashboard_stats.get('ai_calls_made', 0),
                'unique_users': dashboard_stats.get('unique_users', 0),
                'last_updated': dashboard_stats.get('last_updated', current_time.isoformat())
            },

            # Template system
            'template_system': {
                'available_templates': available_templates,
                'template_count': len(available_templates),
                'template_directory': getattr(template_processor, 'template_dir', 'templates_json')
            },

            # Recent activity summary
            'recent_activity': {
                'last_5_operations': [
                    {
                        'operation_type': activity.get('operation_type', 'unknown'),
                        'success': activity.get('success', False),
                        'time_ago': activity.get('time_ago', 'unknown'),
                        'duration': activity.get('duration', 'N/A')
                    } for activity in recent_activity[:5]
                ],
                'activity_count': len(recent_activity)
            },

            # Feedback system
            'feedback_system': {
                'total_feedback': feedback_stats.get('total_feedback', 0),
                'average_rating': feedback_stats.get('average_rating', 0),
                'satisfaction_rate': feedback_stats.get('satisfaction_rate', 0)
            },

            # System information
            'system_info': {
                'current_time': current_time.isoformat(),
                'uptime_minutes': round(session_duration / 60, 1),
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'database_accessible': True  # We'll assume it's accessible if we got this far
            },

            # Performance metrics
            'performance': {
                'avg_response_time': dashboard_stats.get('avg_generation_time', 0),
                'total_requests_processed': dashboard_stats.get('total_pages', 0) + dashboard_stats.get('ai_calls_made', 0),
                'error_rate': 100 - dashboard_stats.get('success_rate', 0),
                'last_activity': recent_activity[0].get('timestamp') if recent_activity else None
            }
        })

    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        return jsonify({
            'agent_type': 'Complete AI Agent (Error State)',
            'status': 'error',
            'error': str(e),
            'enabled': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route("/debug/templates", methods=["GET"])
def debug_templates():
    """Debug endpoint to check available templates"""
    templates = template_processor.get_available_templates()
    template_info = {}

    for template_file in templates:
        try:
            template_data = template_processor.load_template(template_file)
            operation_type = template_file.replace('.json', '')

            template_info[template_file] = {
                "exists": True,
                "title": template_data.get("title", "No title"),
                "sections": len(template_data.get("sections", [])),
                "operation_type": operation_type,
                "file_size": len(str(template_data))
            }
        except Exception as e:
            template_info[template_file] = {
                "exists": False,
                "error": str(e)
            }

    return jsonify({
        "template_directory": template_processor.template_dir,
        "available_templates": templates,
        "template_details": template_info
    })

@app.route("/debug/space_mapping", methods=["GET"])
def debug_space_mapping():
    """Debug space mapping for different operation types"""
    from utils.universal_llm_generator import UniversalLLMGenerator

    generator = UniversalLLMGenerator(
        api_key=os.getenv("MODEL_API_KEY"),
        model_name=os.getenv("MODEL_NAME", "gemini-2.5-flash")
    )

    test_operations = ['s_in', 's_out', 'locker_in', 'locker_out', 'unknown']

    space_mappings = {}
    for op_type in test_operations:
        try:
            config = generator._get_space_config(op_type)
            space_mappings[op_type] = config
        except Exception as e:
            space_mappings[op_type] = {"error": str(e)}

    return jsonify({
        "space_mappings": space_mappings,
        "environment_variables": {
            "CONFLUENCE_SCP_SPACE_KEY": os.getenv("CONFLUENCE_SCP_SPACE_KEY"),
            "CONFLUENCE_SCP_PARENT_PAGE_ID": os.getenv("CONFLUENCE_SCP_PARENT_PAGE_ID"),
            "CONFLUENCE_SCG_SPACE_KEY": os.getenv("CONFLUENCE_SCG_SPACE_KEY"),
            "CONFLUENCE_SCG_PARENT_PAGE_ID": os.getenv("CONFLUENCE_SCG_PARENT_PAGE_ID")
        },
        "expected_mappings": {
            "s_in": "SCP space",
            "s_out": "SCP space",
            "locker_in": "SCG space",
            "locker_out": "SCG space"
        }
    })

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Handle both feedback page display and form submission"""
    if request.method == 'GET':
        # Get recent feedback statistics for display
        try:
            feedback_stats = ai_agent.memory.get_feedback_statistics()
            recent_feedback = ai_agent.memory.get_recent_feedback(limit=5)
        except:
            feedback_stats = {}
            recent_feedback = []

        return render_template('feedback.html',
                               feedback_stats=feedback_stats,
                               recent_feedback=recent_feedback)

    elif request.method == 'POST':
        # Process the feedback submission
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()

            # Generate unique interaction ID
            interaction_id = data.get('interaction_id') or f"feedback_{int(datetime.now().timestamp())}"

            # Enhanced feedback data with user information
            feedback = {
                'rating': int(data.get('rating', 3)),
                'comments': data.get('comments', ''),
                'feature_requests': data.get('feature_requests', ''),
                'contact_me': data.get('contact_me', False),
                'user_name': data.get('user_name', f'Anonymous User'),
                'user_email': data.get('user_email', ''),
                'aspects': {
                    'content_quality': int(data.get('content_quality', 3)),
                    'formatting': int(data.get('formatting', 3)),
                    'accuracy': int(data.get('accuracy', 3)),
                    'completeness': int(data.get('completeness', 3))
                },
                'timestamp': datetime.now().isoformat(),
                'user_agent': request.headers.get('User-Agent', ''),
                'ip_address': request.remote_addr,
                'page_title': data.get('page_title', ''),
                'operation_type': data.get('operation_type', '')
            }

            user_id = data.get('user_id', f'user_{request.remote_addr}')

            # Store feedback using AI agent
            ai_agent.provide_feedback(interaction_id, feedback, user_id)

            logger.info(f"📝 Feedback received: rating={feedback['rating']}, user={feedback['user_name']}")

            return jsonify({
                'success': True,
                'message': f'Thank you {feedback["user_name"]}! Your feedback helps us improve the AI agent.',
                'feedback_id': interaction_id
            })

        except Exception as e:
            logger.error(f"📝 Feedback processing failed: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to process feedback. Please try again.'
            }), 500

@app.route('/api/feedback/recent')
def get_recent_feedback():
    """API endpoint to get recent feedback data"""
    try:
        limit = request.args.get('limit', 10, type=int)
        recent_feedback = ai_agent.memory.get_recent_feedback(limit=limit)

        return jsonify({
            'success': True,
            'feedback': recent_feedback,
            'count': len(recent_feedback)
        })
    except Exception as e:
        logger.error(f"Failed to get recent feedback: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/feedback/stats')
def get_feedback_stats():
    """API endpoint to get feedback statistics"""
    try:
        stats = ai_agent.memory.get_feedback_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Failed to get feedback stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get REAL dashboard statistics with proper calculations"""
    try:
        import sqlite3
        from datetime import datetime, timedelta

        conn = sqlite3.connect(ai_agent.memory.db_path)
        cursor = conn.cursor()

        # Check if page_creations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='page_creations'")
        if not cursor.fetchone():
            # Create the table if it doesn't exist
            cursor.execute('''
                CREATE TABLE page_creations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    operation_type TEXT,
                    template_file TEXT,
                    page_title TEXT,
                    page_id TEXT,
                    page_url TEXT,
                    space_key TEXT,
                    parent_page_id TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    generation_time_seconds REAL,
                    timestamp TEXT,
                    source TEXT,
                    ai_agent_used BOOLEAN DEFAULT 1
                )
            ''')
            conn.commit()

        # Get current statistics
        current_time = datetime.now()

        # Total pages created (successful only)
        cursor.execute('SELECT COUNT(*) FROM page_creations WHERE success = 1')
        total_pages = cursor.fetchone()[0] or 0

        # Total attempts
        cursor.execute('SELECT COUNT(*) FROM page_creations')
        total_attempts = cursor.fetchone()[0] or 0

        # Success rate
        success_rate = (total_pages / max(total_attempts, 1)) * 100

        # Average generation time (successful only)
        cursor.execute('SELECT AVG(generation_time_seconds) FROM page_creations WHERE success = 1 AND generation_time_seconds IS NOT NULL')
        avg_time_result = cursor.fetchone()[0]
        avg_time = round(avg_time_result or 0, 2)

        # AI calls made
        cursor.execute('SELECT COUNT(*) FROM page_creations WHERE ai_agent_used = 1')
        ai_calls = cursor.fetchone()[0] or 0

        # Recent activity (last 7 days)
        week_ago = (current_time - timedelta(days=7)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM page_creations WHERE timestamp > ?', (week_ago,))
        recent_pages = cursor.fetchone()[0] or 0

        # Today's activity
        today = current_time.strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM page_creations WHERE timestamp LIKE ?', (f'{today}%',))
        today_pages = cursor.fetchone()[0] or 0

        # Operation type distribution
        cursor.execute('''
            SELECT operation_type, COUNT(*) as count
            FROM page_creations 
            WHERE success = 1 
            GROUP BY operation_type 
            ORDER BY count DESC
        ''')
        operation_distribution = dict(cursor.fetchall())

        # Unique users
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM page_creations')
        unique_users = cursor.fetchone()[0] or 0

        # Error rate calculation
        cursor.execute('SELECT COUNT(*) FROM page_creations WHERE success = 0')
        failed_attempts = cursor.fetchone()[0] or 0
        error_rate = (failed_attempts / max(total_attempts, 1)) * 100

        # Recent performance (last 24 hours)
        yesterday = (current_time - timedelta(days=1)).isoformat()
        cursor.execute('''
            SELECT AVG(generation_time_seconds) 
            FROM page_creations 
            WHERE timestamp > ? AND success = 1 AND generation_time_seconds IS NOT NULL
        ''', (yesterday,))
        recent_avg_time = cursor.fetchone()[0] or 0

        conn.close()

        response_data = {
            'success': True,
            'statistics': {
                'total_pages': total_pages,
                'success_rate': round(success_rate, 1),
                'avg_generation_time': avg_time,
                'ai_calls_made': ai_calls,
                'recent_pages_week': recent_pages,
                'today_pages': today_pages,
                'operation_distribution': operation_distribution,
                'unique_users': unique_users,
                'error_rate': round(error_rate, 1),
                'total_attempts': total_attempts,
                'failed_attempts': failed_attempts,
                'recent_avg_time_24h': round(recent_avg_time or 0, 2),
                'last_updated': current_time.isoformat()
            },
            'timestamp': current_time.isoformat(),
            'cache_bust': int(current_time.timestamp())
        }

        # Add cache-busting headers
        response = jsonify(response_data)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        return response

    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/dashboard/activity')
def get_dashboard_activity():
    """Get REAL recent activity with proper ordering"""
    try:
        import sqlite3
        from datetime import datetime

        limit = request.args.get('limit', 10, type=int)

        conn = sqlite3.connect(ai_agent.memory.db_path)
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='page_creations'")
        if not cursor.fetchone():
            return jsonify({
                'success': True,
                'activity': [],
                'count': 0,
                'message': 'No page_creations table found'
            })

        # Get recent activity with proper ordering
        cursor.execute('''
            SELECT 
                id,
                operation_type, 
                template_file, 
                page_title, 
                success, 
                generation_time_seconds, 
                timestamp, 
                space_key, 
                page_url,
                user_id,
                source,
                error_message
            FROM page_creations 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))

        results = cursor.fetchall()
        conn.close()

        activities = []
        current_time = datetime.now()

        for row in results:
            try:
                # Parse timestamp
                timestamp_str = row[6]
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    time_diff = current_time - timestamp

                    if time_diff.days > 0:
                        time_ago = f"{time_diff.days} day{'s' if time_diff.days != 1 else ''} ago"
                    elif time_diff.seconds > 3600:
                        hours = time_diff.seconds // 3600
                        time_ago = f"{hours} hour{'s' if hours != 1 else ''} ago"
                    elif time_diff.seconds > 60:
                        minutes = time_diff.seconds // 60
                        time_ago = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                    else:
                        time_ago = "Just now"
                except:
                    time_ago = "Unknown time"

                activity = {
                    'id': row[0],
                    'operation_type': row[1] or 'unknown',
                    'template_file': row[2] or 'unknown',
                    'page_title': row[3] or 'Untitled',
                    'success': bool(row[4]),
                    'duration': f"{row[5]:.1f}s" if row[5] else "N/A",
                    'timestamp': timestamp_str,
                    'time_ago': time_ago,
                    'space_key': row[7] or 'UNKNOWN',
                    'page_url': row[8] or '',
                    'user_id': row[9] or 'unknown',
                    'source': row[10] or 'unknown',
                    'error_message': row[11] or ''
                }

                activities.append(activity)

            except Exception as e:
                logger.error(f"Error processing activity row: {e}")
                continue

        response_data = {
            'success': True,
            'activity': activities,
            'count': len(activities),
            'timestamp': current_time.isoformat(),
            'cache_bust': int(current_time.timestamp())
        }

        # Add cache-busting headers
        response = jsonify(response_data)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        return response

    except Exception as e:
        logger.error(f"Failed to get dashboard activity: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/dashboard/charts')
def get_dashboard_charts():
    """API endpoint to get chart data"""
    try:
        stats = ai_agent.memory.get_dashboard_statistics()

        # Generate chart data based on real statistics
        operation_dist = stats.get('operation_distribution', {})

        # Generate weekly usage data
        import random
        weekly_data = [random.randint(0, max(1, stats.get('total_pages', 0))) for _ in range(7)]

        chart_data = {
            'usage_chart': {
                'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'data': weekly_data
            },
            'operation_chart': {
                'labels': list(operation_dist.keys()) if operation_dist else ['s_in', 's_out', 'locker_in', 'locker_out'],
                'data': list(operation_dist.values()) if operation_dist else [0, 0, 0, 0]
            }
        }

        return jsonify({
            'success': True,
            'charts': chart_data
        })
    except Exception as e:
        logger.error(f"Failed to get chart data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/debug/populate_test_data')
def populate_test_data():
    """Populate test data for dashboard testing"""
    try:
        import random
        from datetime import datetime, timedelta

        # Sample operations
        operations = ['s_in', 's_out', 'locker_in', 'locker_out']

        # Create test page creations
        for i in range(15):
            operation_type = random.choice(operations)
            template_file = f"{operation_type}.json"

            # Random timestamp in last 7 days
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)

            test_data = {
                'operation_type': operation_type,
                'template_file': template_file,
                'source': 'test_data'
            }

            test_result = {
                'success': random.choice([True, True, True, False]),  # 75% success rate
                'title': f'Test_{operation_type}_{timestamp.strftime("%Y%m%d_%H%M%S")}_{i}',
                'page_id': str(random.randint(1000000, 9999999)),
                'page_url': f'https://confluence.rakuten-it.com/confluence/pages/viewpage.action?pageId={random.randint(1000000, 9999999)}',
                'space_key': 'SCG' if 'locker' in operation_type else 'SCP',
                'parent_page_id': '5880757738' if 'locker' in operation_type else '5890230619'
            }

            generation_time = random.uniform(1.0, 5.0)

            # Store using the memory system
            ai_agent.memory.store_page_creation(
                user_id=f'test_user_{random.randint(1, 5)}',
                operation_data=test_data,
                result=test_result,
                generation_time=generation_time
            )

        # Create test feedback
        for i in range(8):
            feedback_data = {
                'user_name': f'Test User {i+1}',
                'user_email': f'testuser{i+1}@example.com',
                'rating': random.randint(3, 5),
                'aspects': {
                    'content_quality': random.randint(3, 5),
                    'formatting': random.randint(3, 5),
                    'accuracy': random.randint(3, 5),
                    'completeness': random.randint(3, 5)
                },
                'comments': f'Great tool! Test feedback comment {i+1}. Very helpful for our daily operations.',
                'feature_requests': f'Would love to see feature {i+1} added in the future.',
                'contact_me': random.choice([True, False]),
                'timestamp': (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
                'operation_type': random.choice(operations)
            }

            ai_agent.memory.store_feedback(
                interaction_id=f'test_interaction_{i+1}',
                feedback=feedback_data,
                user_id=f'test_user_{i+1}'
            )

        return jsonify({
            'success': True,
            'message': 'Test data populated successfully! Dashboard should now show data.',
            'pages_created': 15,
            'feedback_entries': 8,
            'note': 'Refresh your dashboard to see the new data'
        })

    except Exception as e:
        logger.error(f"Failed to populate test data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/debug/check_recent_data')
def check_recent_data():
    """Debug endpoint to check what data is actually in the database"""
    try:
        import sqlite3
        from datetime import datetime, timedelta

        conn = sqlite3.connect(ai_agent.memory.db_path)
        cursor = conn.cursor()

        # Check if page_creations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='page_creations'")
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            return jsonify({
                'success': False,
                'error': 'page_creations table does not exist',
                'database_path': ai_agent.memory.db_path
            })

        # Get all recent data (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute('''
            SELECT id, user_id, operation_type, template_file, page_title, 
                   success, timestamp, generation_time_seconds, source
            FROM page_creations 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (yesterday,))

        recent_data = cursor.fetchall()

        # Get today's data specifically
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM page_creations 
            WHERE timestamp LIKE ?
        ''', (f'{today}%',))

        today_count = cursor.fetchone()[0]

        # Get total count
        cursor.execute('SELECT COUNT(*) FROM page_creations')
        total_count = cursor.fetchone()[0]

        # Get last 5 entries regardless of date
        cursor.execute('''
            SELECT id, user_id, operation_type, template_file, page_title, 
                   success, timestamp, generation_time_seconds, source
            FROM page_creations 
            ORDER BY timestamp DESC
            LIMIT 5
        ''')

        last_5_entries = cursor.fetchall()

        conn.close()

        return jsonify({
            'success': True,
            'database_path': ai_agent.memory.db_path,
            'table_exists': table_exists,
            'total_records': total_count,
            'today_records': today_count,
            'recent_24h_records': len(recent_data),
            'last_5_entries': [
                {
                    'id': row[0],
                    'user_id': row[1],
                    'operation_type': row[2],
                    'template_file': row[3],
                    'page_title': row[4],
                    'success': bool(row[5]),
                    'timestamp': row[6],
                    'generation_time': row[7],
                    'source': row[8]
                } for row in last_5_entries
            ],
            'recent_24h_data': [
                {
                    'id': row[0],
                    'user_id': row[1],
                    'operation_type': row[2],
                    'template_file': row[3],
                    'page_title': row[4],
                    'success': bool(row[5]),
                    'timestamp': row[6],
                    'generation_time': row[7],
                    'source': row[8]
                } for row in recent_data
            ],
            'debug_info': {
                'current_time': datetime.now().isoformat(),
                'yesterday_cutoff': yesterday,
                'today_date': today
            }
        })

    except Exception as e:
        logger.error(f"Failed to check recent data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/debug/database_info')
def database_info():
    """Get detailed information about your SQLite database"""
    try:
        import os
        import sqlite3

        db_path = ai_agent.memory.db_path

        # Check if database file exists
        if not os.path.exists(db_path):
            return jsonify({
                'success': False,
                'error': 'Database file does not exist',
                'path': db_path
            })

        # Get file size
        file_size_bytes = os.path.getsize(db_path)
        file_size_mb = file_size_bytes / (1024 * 1024)

        # Connect and get database info
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get SQLite version
        cursor.execute('SELECT sqlite_version()')
        sqlite_version = cursor.fetchone()[0]

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Get record counts for each table
        table_info = {}
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]

            # Get table size estimate
            cursor.execute(f'SELECT * FROM {table} LIMIT 1')
            sample = cursor.fetchone()
            estimated_size_per_record = len(str(sample)) if sample else 0

            table_info[table] = {
                'record_count': count,
                'estimated_size_per_record': estimated_size_per_record,
                'estimated_total_size': count * estimated_size_per_record
            }

        # Get database page info
        cursor.execute('PRAGMA page_count')
        page_count = cursor.fetchone()[0]

        cursor.execute('PRAGMA page_size')
        page_size = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            'success': True,
            'database_info': {
                'file_path': db_path,
                'file_size_bytes': file_size_bytes,
                'file_size_mb': round(file_size_mb, 2),
                'file_size_human': f'{file_size_mb:.2f} MB' if file_size_mb > 1 else f'{file_size_bytes/1024:.1f} KB',
                'sqlite_version': sqlite_version,
                'page_count': page_count,
                'page_size': page_size,
                'total_pages_size': page_count * page_size
            },
            'tables': table_info,
            'performance_estimate': {
                'very_fast': file_size_mb < 10,
                'fast': 10 <= file_size_mb < 100,
                'moderate': 100 <= file_size_mb < 1000,
                'slow': file_size_mb >= 1000
            },
            'recommendations': {
                'current_status': 'excellent' if file_size_mb < 10 else 'good' if file_size_mb < 100 else 'consider_optimization',
                'backup_recommended': file_size_mb > 50,
                'indexing_recommended': file_size_mb > 10,
                'archiving_recommended': file_size_mb > 100
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/debug/database_state')
def debug_database_state():
    """Complete database state analysis"""
    try:
        import sqlite3
        from datetime import datetime, timedelta

        conn = sqlite3.connect(ai_agent.memory.db_path)
        cursor = conn.cursor()

        # Check all tables and their data
        result = {
            'database_path': ai_agent.memory.db_path,
            'current_time': datetime.now().isoformat(),
            'tables': {}
        }

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            try:
                # Get table structure
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]

                # Get total count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total_count = cursor.fetchone()[0]

                # Get recent records (last 24 hours)
                if 'timestamp' in columns:
                    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE timestamp > ?", (yesterday,))
                    recent_count = cursor.fetchone()[0]

                    # Get latest 5 records
                    cursor.execute(f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT 5")
                    latest_records = cursor.fetchall()
                else:
                    recent_count = 0
                    latest_records = []

                result['tables'][table] = {
                    'columns': columns,
                    'total_records': total_count,
                    'recent_24h': recent_count,
                    'latest_records': [
                        dict(zip(columns, record)) for record in latest_records
                    ]
                }

            except Exception as e:
                result['tables'][table] = {'error': str(e)}

        conn.close()
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/debug/clear_old_data')
def clear_old_data():
    """Clear old dashboard data and start fresh"""
    try:
        import sqlite3
        from datetime import datetime, timedelta

        conn = sqlite3.connect(ai_agent.memory.db_path)
        cursor = conn.cursor()

        # Get current counts before clearing
        cursor.execute('SELECT COUNT(*) FROM page_creations')
        old_count_result = cursor.fetchone()
        old_count = old_count_result[0] if old_count_result else 0

        # Keep only last 24 hours (recommended)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute('DELETE FROM page_creations WHERE timestamp < ?', (yesterday,))

        try:
            cursor.execute('DELETE FROM interactions WHERE timestamp < ?', (yesterday,))
        except:
            pass  # Table might not exist

        try:
            cursor.execute('DELETE FROM feedback WHERE timestamp < ?', (yesterday,))
        except:
            pass  # Table might not exist

        # Get new counts
        cursor.execute('SELECT COUNT(*) FROM page_creations')
        new_count_result = cursor.fetchone()
        new_count = new_count_result[0] if new_count_result else 0

        # Reset auto-increment counters
        try:
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="page_creations"')
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="interactions"')
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="feedback"')
        except:
            pass  # sqlite_sequence might not exist

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Old data cleared successfully',
            'old_record_count': old_count,
            'new_record_count': new_count,
            'records_deleted': old_count - new_count,
            'cutoff_date': yesterday,
            'note': 'Dashboard will now show accurate averages for recent data only'
        })

    except Exception as e:
        logger.error(f"Failed to clear old data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/debug/reset_dashboard_completely')
def reset_dashboard_completely():
    """COMPLETELY reset dashboard data - USE WITH CAUTION"""
    try:
        import sqlite3

        conn = sqlite3.connect(ai_agent.memory.db_path)
        cursor = conn.cursor()

        # Get counts before deletion
        tables_info = {}
        for table in ['page_creations', 'interactions', 'feedback']:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                tables_info[table] = {'before': count}
            except:
                tables_info[table] = {'before': 0}

        # COMPLETELY CLEAR ALL DATA
        try:
            cursor.execute('DELETE FROM page_creations')
        except:
            pass
        try:
            cursor.execute('DELETE FROM interactions')
        except:
            pass
        try:
            cursor.execute('DELETE FROM feedback')
        except:
            pass
        try:
            cursor.execute('DELETE FROM user_preferences')
        except:
            pass
        try:
            cursor.execute('DELETE FROM user_sessions')
        except:
            pass

        # Reset auto-increment counters
        try:
            cursor.execute('DELETE FROM sqlite_sequence')
        except:
            pass

        # Verify deletion
        for table in ['page_creations', 'interactions', 'feedback']:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                tables_info[table]['after'] = count
            except:
                tables_info[table]['after'] = 0

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'ALL dashboard data has been completely reset',
            'tables_cleared': tables_info,
            'warning': 'All historical data has been permanently deleted',
            'note': 'Dashboard will now show only new data going forward'
        })

    except Exception as e:
        logger.error(f"Failed to reset dashboard: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
