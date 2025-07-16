# main.py

from flask import Flask, jsonify, request
import openai
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

def process_chat(message, data):
  rakuten_url = "https://api.ai.public.rakuten-it.com/openai/v1/"
  service_account_key = "raik-sk-adf42e626r10aie9a6598cad9c615e1cfd340dec18b64be9a6598cad9c615e1c"

  openai.base_url = rakuten_url
  openai.api_key = service_account_key
  if not openai.api_key:
    print("Error: OpenAI API key not found.  Set the OPENAI_API_KEY environment variable.")
    return None

  prompt = """Act as a helpful chatbot assistant for users who are not very technical. When you receive a message input and accompanying data from the user, analyze the message, reason through the information, and then provide a specific, easy-to-understand response tailored to the user's needs. # Steps 1. Carefully read and understand the user's message and any provided data. 2. Identify key points or questions raised by the user. 3. Reason through the available data and any relevant context. 4. Break down complex concepts into simple, clear explanations suitable for non-technical users. 5. Deliver your response in a concise and friendly manner, ensuring clarity and specificity. # Output Format Respond with a brief paragraph of 2-4 sentences. Use plain language and avoid technical jargon. Make sure the explanation directly addresses the user's message and needs. # Examples **Example 1** - User input: "Why can't I log into my account?" - Data: "Login failed due to incorrect password." - Output: You are seeing this error because the password you entered does not match the one on your account. Please double-check your password or use the 'Forgot password' option to reset it if needed. **Example 2** - User input: "How can I get my order status?" - Data: "Order #1234 is being processed and will ship in two days." - Output: Your order is currently being prepared and will be shipped in about two days. You’ll get an email with tracking information as soon as it’s on its way. # Notes - Always begin your response with a brief reasoning or explanation before giving any conclusions or advice. - If no data is provided, acknowledge this and answer based on the message alone. - If the user's question is ambiguous, ask for clarification in simple terms."""
  try:
    completion = openai.chat.completions.create(
      model="gpt-4.1",
      messages=[
        {
          "role": "user",
          "content": f"{prompt}\n\nMessage: {message}\nFiltered Data:\n{json.dumps(data, indent=2)}"
        }
      ]
    )

    response_text = completion.choices[0].message.content
    return response_text

  except Exception as e:
    print(f"Error during OpenAI analysis: {e}")
    return None

@app.route('/analyze', methods=['POST'])
def chat_endpoint():
  try:
    req_data = request.get_json()
    message = req_data.get('message')
    data = req_data.get('data')

    analysis = process_chat(message, data)
    return jsonify({"analysis": analysis}), 200
  except Exception as e:
    return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
  print("Application has started")
  app.run(debug=True)
