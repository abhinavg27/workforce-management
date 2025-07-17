# Chatbot Service

This folder contains the implementation of a Flask-based chatbot service that integrates with the OpenAI API to process user messages and provide helpful responses.

## Features

- **Flask Framework**: Lightweight web framework for building the chatbot API.
- **CORS Support**: Enabled using `flask-cors` to allow cross-origin requests.
- **OpenAI Integration**: Uses OpenAI's API to generate responses based on user input and accompanying data.
- **RESTful Endpoint**: Provides a `/analyze` endpoint for processing chat messages.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Flask and required dependencies (see `requirements.txt`)

## Installation

1. Clone the repository and navigate to the `chatbot` folder:
   ```bash
   git clone <repository-url>
   cd chatbot
2. Create a virtual environment and activate it:  
    ```bash
    python3 -m venv venv
    source venv/bin/activate
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt

## Usage

1. Start the Flask application: 
    ```bash
   python main.py
   The Flask application will start on http://127.0.0.1:5000.
2. Send a POST request to the /analyze endpoint with the following JSON payload:
   ```json
   {
     "message": "Your message here",
     "data": { "key": "value" }
   }
   ```

The chatbot will return a JSON response with the analysis.

## Example Response
```json
{
  "analysis": "You asked for workers who are under 25 years old. From the information given, only Nina Reed is under 25, with an age of 24. If you need more details about Nina or information on other workers, please let me know!"
}
```

## Dependencies
The required Python packages are listed in requirements.txt. Install them using pip. 