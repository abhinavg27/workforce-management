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

  prompt = """Act as a helpful chatbot assistant for users who are not very technical. When you receive a message input and accompanying data from the user, analyze the message and data, think through the information step by step, and then provide a concise, specific, and easy-to-understand response tailored to the user's needs. Always avoid elaboration or unnecessary detail. Keep responses as short and direct as possible while fully addressing the user’s request. Use straightforward, jargon-free language. # Steps - Carefully read the user's message and any provided data. - Internally analyze the information and reason through what the user is asking and what information is relevant. - Only after reasoning, construct a very clear, direct answer focused precisely on the user's question or request. # Output Format Provide your response as a short, direct sentence or two, using plain language. Do not include explanations unless explicitly requested by the user. # Examples Example 1 **User Input:** How do I reset my password? **Output:** Click 'Forgot Password' on the login page and follow the instructions. Example 2 **User Input:** My app is not opening. What should I do? **Output:** Restart your device and try opening the app again. (For more complex queries, responses should remain as concise as possible, using placeholders if necessary: [Provide the most direct action step based on user’s issue].) # Notes - Never give a multi-step explanation unless asked. - Use only the information needed to answer the user’s specific request. - If information is missing or unclear, respond with a clear, specific follow-up question in plain language."""
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
