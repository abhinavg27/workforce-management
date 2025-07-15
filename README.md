# 🤖 Confluence AI Agent

An intelligent AI agent for automated Confluence page generation with learning capabilities.

## ✨ Features

- 🧠 **AI-Powered**: Uses Google Gemini for intelligent content generation
- 📚 **Learning**: Learns from user interactions and feedback
- 🎯 **Template-Agnostic**: Handles any JSON template structure
- 🔄 **Adaptive**: Improves over time with usage patterns
- 🛡️ **Safe**: Bulletproof HTML generation
- 🌐 **Multi-Space**: Supports multiple Confluence spaces

## 🚀 Quick Start

This project provides a web interface for creating Confluence pages using an AI agent. It supports multiple page formats (meeting notes, release notes) and uses Flask for the web interface, the `requests` library for interacting with the Confluence API, and `lxml` for XML manipulation.

## Setup

1.  **Clone the repository:** `git clone <your_repository_url>`
2.  **Create a virtual environment:** `python -m venv venv`
3.  **Activate the virtual environment:**
    *   On Windows: `venv\Scripts\activate`
    *   On macOS/Linux: `source venv/bin/activate`
4.  **Install dependencies:** `pip install -r requirements.txt`
5.  **Create a `.env` file** in the root directory and add your Confluence API key, space key, and domain:

    ```
    CONFLUENCE_SPACE_KEY="YOUR_CONFLUENCE_SPACE_KEY"
    CONFLUENCE_API_TOKEN="YOUR_CONFLUENCE_API_TOKEN"
    CONFLUENCE_DOMAIN="YOUR_CONFLUENCE_DOMAIN.atlassian.net"
    ```

6.  **(Optional) If using OpenAI, add your Gemini API key to the `.env` file:**

    ```
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    ```

7.  **Run the application:** `python app.py`
8.  **Access the application:** Open your web browser and go to `http://127.0.0.1:5000/`

## Configuration

*   **CONFLUENCE_SPACE_KEY:** Your Confluence space key.
*   **CONFLUENCE_API_TOKEN:** Your Confluence API token.
*   **CONFLUENCE_DOMAIN:** Your Confluence domain (e.g., "yourcompany.atlassian.net").
*   **OPENAI_API_KEY:** (Optional) Your OpenAI API key if you're using OpenAI.

## Important Notes

*   Replace the placeholder `generate_content_with_llm` function with your actual LLM integration code.
*   This is a more advanced example and includes basic support for multiple page formats.
*   Do not hardcode API keys or sensitive data in your code. Use environment variables instead.
*   Disable debug mode in production.