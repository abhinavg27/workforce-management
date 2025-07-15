import json
import os
import logging
from datetime import datetime, timedelta
import re
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class TemplateProcessor:
    def __init__(self, template_dir="page_templates"):
        self.template_dir = template_dir
        logger.info(f"Initialized TemplateProcessor with directory: {self.template_dir}")
        if not os.path.exists(self.template_dir):
            logger.error(f"Template directory does not exist: {self.template_dir}")
            os.makedirs(self.template_dir)
            logger.info(f"Created template directory: {self.template_dir}")

    def load_template(self, template_name:str) -> Optional[Dict]:
        """Load template from JSON file"""
        template_path = os.path.join(self.template_dir, template_name)
        logger.info(f"Attempting to load template: {template_path}")

        try:
            if not os.path.exists(template_path):
                logger.error(f"Template file not found: {template_path}")
                return None
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                logger.info(f"Successfully loaded template: {template_name}")
                return template_data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {template_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            return None

    def get_available_templates(self) -> List[str]:
        """Get list of available template files"""
        try:
            if not os.path.exists(self.template_dir):
                logger.warning(f"Template directory {self.template_dir} does not exist")
                return []

            templates = [f for f in os.listdir(self.template_dir)
                         if f.endswith('.json') and os.path.isfile(os.path.join(self.template_dir, f))]
            logger.info(f"Found {len(templates)} templates: {templates}")
            return sorted(templates)
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            return []

def parse_operation_from_promptold(self, prompt):
    """Enhanced parsing that can extract just dates or full operation details"""

    # Convert to lowercase for easier matching
    prompt_lower = prompt.lower().strip()

    # Operation type patterns
    operation_patterns = {
        's_in': ['s_in', 's-in', 'sin', 'shop in', 'shop ingestion', 'scp in'],
        's_out': ['s_out', 's-out', 'sout', 'shop out', 'shop outgestion', 'scp out'],
        'locker_in': ['locker_in', 'locker-in', 'locker in'],
        'locker_out': ['locker_out', 'locker-out', 'locker out', 'scg out']
    }

    # Find operation type
    operation_type = None
    template_file = None

    for op_type, patterns in operation_patterns.items():
        if any(pattern in prompt_lower for pattern in patterns):
            operation_type = op_type
            template_file = f"{op_type}.json"
            break

    # Date extraction patterns
    operation_date = None
    display_date = None

    # Try to extract dates from prompt
    import re
    from datetime import datetime, timedelta

    # Pattern 1: YYYYMMDD format
    date_match = re.search(r'\b(\d{8})\b', prompt)
    if date_match:
        operation_date = date_match.group(1)
        try:
            parsed_date = datetime.strptime(operation_date, "%Y%m%d")
            display_date = parsed_date.strftime("%d %B %Y")
        except:
            pass

    # Pattern 2: Relative dates
    if 'today' in prompt_lower:
        today = datetime.now()
        operation_date = today.strftime("%Y%m%d")
        display_date = today.strftime("%d %B %Y")
    elif 'tomorrow' in prompt_lower:
        tomorrow = datetime.now() + timedelta(days=1)
        operation_date = tomorrow.strftime("%Y%m%d")
        display_date = tomorrow.strftime("%d %B %Y")
    elif 'yesterday' in prompt_lower:
        yesterday = datetime.now() - timedelta(days=1)
        operation_date = yesterday.strftime("%Y%m%d")
        display_date = yesterday.strftime("%d %B %Y")

    # Pattern 3: Natural language dates
    date_patterns = [
        (r'(\d{1,2})\s+(january|jan)', lambda m: self._parse_natural_date(m, 1)),
        (r'(\d{1,2})\s+(february|feb)', lambda m: self._parse_natural_date(m, 2)),
        (r'(\d{1,2})\s+(march|mar)', lambda m: self._parse_natural_date(m, 3)),
        (r'(\d{1,2})\s+(april|apr)', lambda m: self._parse_natural_date(m, 4)),
        (r'(\d{1,2})\s+(may)', lambda m: self._parse_natural_date(m, 5)),
        (r'(\d{1,2})\s+(june|jun)', lambda m: self._parse_natural_date(m, 6)),
        (r'(\d{1,2})\s+(july|jul)', lambda m: self._parse_natural_date(m, 7)),
        (r'(\d{1,2})\s+(august|aug)', lambda m: self._parse_natural_date(m, 8)),
        (r'(\d{1,2})\s+(september|sep)', lambda m: self._parse_natural_date(m, 9)),
        (r'(\d{1,2})\s+(october|oct)', lambda m: self._parse_natural_date(m, 10)),
        (r'(\d{1,2})\s+(november|nov)', lambda m: self._parse_natural_date(m, 11)),
        (r'(\d{1,2})\s+(december|dec)', lambda m: self._parse_natural_date(m, 12)),
    ]

    for pattern, parser in date_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            try:
                operation_date, display_date = parser(match)
                break
            except:
                continue

    return operation_type, template_file, operation_date, display_date

# In template_processor.py - Enhanced date parsing:

# Add this method to your TemplateProcessor class in template_processor.py

def parse_operation_from_prompt(self, prompt):
    """Parse operation type and dates from user prompt"""

    prompt_lower = prompt.lower().strip()
    logger.info(f"🧠 Parsing prompt: {prompt}")

    # Operation type patterns
    operation_patterns = {
        's_in': ['s_in', 's-in', 'sin', 'shop in', 'shop ingestion', 'scp in', 's in'],
        's_out': ['s_out', 's-out', 'sout', 'shop out', 'shop outgestion', 'scp out', 's out'],
        'locker_in': ['locker_in', 'locker-in', 'locker in'],
        'locker_out': ['locker_out', 'locker-out', 'locker out', 'scg out']
    }

    # Find operation type
    operation_type = None
    template_file = None

    for op_type, patterns in operation_patterns.items():
        if any(pattern in prompt_lower for pattern in patterns):
            operation_type = op_type
            template_file = f"{op_type}.json"
            logger.info(f"🧠 Found operation type: {operation_type}")
            break

    # Date extraction
    operation_date = None
    display_date = None

    import re
    from datetime import datetime, timedelta

    # Relative dates
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

def _parse_natural_date(self, match, month):
    """Parse natural language date"""
    day = int(match.group(1))
    year = datetime.now().year

    try:
        date_obj = datetime(year, month, day)
        operation_date = date_obj.strftime("%Y%m%d")
        display_date = date_obj.strftime("%d %B %Y")
        return operation_date, display_date
    except:
        return None, None

    def _parse_date_from_prompt(self, prompt_lower):
        """Parse date from prompt with multiple format support"""
        current_date = datetime.now()

        # Handle "today"
        if 'today' in prompt_lower:
            operation_date = current_date.strftime("%Y%m%d")
            display_date = current_date.strftime("%d %B %Y")
            logger.info(f"Parsed 'today': {operation_date} -> {display_date}")
            return operation_date, display_date

        # Handle "tomorrow"
        if 'tomorrow' in prompt_lower:
            tomorrow = current_date + timedelta(days=1)
            operation_date = tomorrow.strftime("%Y%m%d")
            display_date = tomorrow.strftime("%d %B %Y")
            logger.info(f"Parsed 'tomorrow': {operation_date} -> {display_date}")
            return operation_date, display_date

        # Handle specific dates like "July 3rd", "July 3", "3rd July"
        date_match = self._extract_specific_date(prompt_lower, current_date.year)
        if date_match:
            return date_match

        # Handle month names (July, December, etc.)
        month_match = self._extract_month_date(prompt_lower, current_date)
        if month_match:
            return month_match

        # Handle relative dates like "next week", "next month"
        relative_match = self._extract_relative_date(prompt_lower, current_date)
        if relative_match:
            return relative_match

        # Default to today if no date found
        operation_date = current_date.strftime("%Y%m%d")
        display_date = current_date.strftime("%d %B %Y")
        logger.info(f"No specific date found, using today: {operation_date} -> {display_date}")
        return operation_date, display_date

    def _extract_specific_date(self, prompt_lower, current_year):
        """Extract specific dates like 'July 3rd', 'July 3', '3rd July'"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }

        # Pattern for "July 3rd", "July 3", "December 25th"
        pattern1 = r'(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?'
        match1 = re.search(pattern1, prompt_lower)

        if match1:
            month_name = match1.group(1)
            day = int(match1.group(2))

            if month_name in months:
                month = months[month_name]

                # Determine year (if month has passed, use next year)
                current_month = datetime.now().month
                year = current_year if month >= current_month else current_year + 1

                try:
                    target_date = datetime(year, month, day)
                    operation_date = target_date.strftime("%Y%m%d")
                    display_date = target_date.strftime("%d %B %Y")
                    logger.info(f"Parsed specific date '{match1.group(0)}': {operation_date} -> {display_date}")
                    return operation_date, display_date
                except ValueError:
                    logger.warning(f"Invalid date: {year}-{month}-{day}")

        # Pattern for "3rd July", "25th December"
        pattern2 = r'(\d{1,2})(?:st|nd|rd|th)?\s+(\w+)'
        match2 = re.search(pattern2, prompt_lower)

        if match2:
            day = int(match2.group(1))
            month_name = match2.group(2)

            if month_name in months:
                month = months[month_name]

                # Determine year
                current_month = datetime.now().month
                year = current_year if month >= current_month else current_year + 1

                try:
                    target_date = datetime(year, month, day)
                    operation_date = target_date.strftime("%Y%m%d")
                    display_date = target_date.strftime("%d %B %Y")
                    logger.info(f"Parsed specific date '{match2.group(0)}': {operation_date} -> {display_date}")
                    return operation_date, display_date
                except ValueError:
                    logger.warning(f"Invalid date: {year}-{month}-{day}")

        return None

    def _extract_month_date(self, prompt_lower, current_date):
        """Extract month-only dates like 'July', 'December'"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }

        for month_name, month_num in months.items():
            if month_name in prompt_lower:
                current_month = current_date.month
                current_year = current_date.year

                # If target month is in the past, use next year
                year = current_year if month_num >= current_month else current_year + 1

                # Use first day of the month
                operation_date = f"{year}{month_num:02d}01"
                display_date = f"01 {month_name.capitalize()} {year}"
                logger.info(f"Parsed month '{month_name}': {operation_date} -> {display_date}")
                return operation_date, display_date

        return None

    def _extract_relative_date(self, prompt_lower, current_date):
        """Extract relative dates like 'next week', 'next month'"""
        if 'next week' in prompt_lower:
            next_week = current_date + timedelta(weeks=1)
            operation_date = next_week.strftime("%Y%m%d")
            display_date = next_week.strftime("%d %B %Y")
            logger.info(f"Parsed 'next week': {operation_date} -> {display_date}")
            return operation_date, display_date

        if 'next month' in prompt_lower:
            # Go to first day of next month
            if current_date.month == 12:
                next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                next_month = current_date.replace(month=current_date.month + 1, day=1)

            operation_date = next_month.strftime("%Y%m%d")
            display_date = next_month.strftime("%d %B %Y")
            logger.info(f"Parsed 'next month': {operation_date} -> {display_date}")
            return operation_date, display_date

        return None

    def format_date(self, date_str, format_type="display"):
        """Format date string"""
        try:
            if len(date_str) == 8:  # YYYYMMDD
                dt = datetime.strptime(date_str, "%Y%m%d")
                if format_type == "display":
                    return dt.strftime("%d %B %Y")
                return dt.strftime("%Y%m%d")
        except:
            pass
        return date_str
