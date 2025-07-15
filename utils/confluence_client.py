import logging
import traceback

import requests
from atlassian import Confluence
from typing import Dict, Optional
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


load_dotenv()

class ConfluenceClient:
    """Confluence client with authentication for creating pages"""

    def __init__(self, url: str, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Confluence client with username and API token/password.

        Args:
            url (str): Confluence server URL (e.g., https://confluence.rakuten-it.com/confluence)
            username (str, optional): Confluence username
            password (str, optional): Confluence API token or password
        """
        self.url = url.rstrip('/')
        self.username = username or os.getenv("CONFLUENCE_USERNAME")
        #self.api_token = api_token or os.getenv("CONFLUENCE_API_TOKEN")
        self.password =os.getenv("CONFLUENCE_PASSWORD")
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        logger.info(f"Initialized ConfluenceClient for {url}")

        if not self.username or not self.password:
            logger.error("🔗 Missing Confluence credentials")
            raise ValueError("Confluence username and API token/password are required")

        try:
            self.confluence = Confluence(
                url=self.url,
                username=self.username,
                password=self.password,  # API token or password
                verify_ssl=True
            )
            logger.info(f"🔗 Confluence client initialized WITH authentication for {self.url}")
        except Exception as e:
            logger.error(f"🔗 Failed to initialize Confluence client: {e}\n{traceback.format_exc()}")
            raise RuntimeError(f"Confluence client initialization failed: {str(e)}")

    def create_page(self, space_key: str, title: str, content: str, parent_id: Optional[str] = None) -> Dict:
        """
        Create a Confluence page in the specified space.

        Args:
            space_key (str): Confluence space key (e.g., 'SCP')
            title (str): Page title
            content (str): Page content in storage format
            parent_id (str, optional): Parent page ID

        Returns:
            Dict: Page creation result with success status, page ID, and URL
        """
        try:
            logger.info(f"📝 Creating page: '{title}' in space '{space_key}'")
            endpoint = f"{self.url}/rest/api/content"
            page_data = {
                'type': 'page',
                'space': {'key': space_key},
                'title': title,
                'body': {'storage': {'value': content, 'representation': 'storage'}}
            }
            if parent_id:
                page_data['ancestors'] = [{'id': parent_id}]

            response = self.confluence.create_page(
                space=space_key,
                title=title,
                body=content,
                parent_id=parent_id,
                representation='storage'
            )
            page_url = f"{self.url}{response['_links']['webui']}"

            #response = self.session.post(endpoint, json=page_data)
            #response.raise_for_status()
            #result = response.json()
            #logger.info(f"Created page '{title}' in space '{space_key}'")
            #page_url = f"{self.url}{response['_links']['webui']}"

            logger.info(f"✅ Page created successfully: ID={response['id']}, URL={page_url}")
            return {
                'success': True,
                'page_id': response['id'],
                'page_url': page_url,
                'title': title,
                'space_key': space_key,
                'mock_mode': False
            }
        except Exception as e:
            logger.error(f"❌ Page creation failed: {e}\n{traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e),
                'page_id': None,
                'page_url': None,
                'mock_mode': False
            }

    def test_connection(self) -> Dict:
        """
        Test connection to Confluence server.

        Returns:
            Dict: Connection test result
        """
        try:
            logger.info("🔗 Testing connection")
            self.confluence.get_all_spaces(limit=1)  # Minimal API call to test
            return {
                'success': True,
                'message': f'Connection test successful for {self.url}',
                'url': self.url,
                'authenticated': True,
                'mock_mode': False
            }
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}\n{traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e),
                'mock_mode': False
            }