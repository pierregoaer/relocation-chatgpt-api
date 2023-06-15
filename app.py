from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app, origins='*')
openai.api_key = os.environ['OPENAI_API_KEY']


@app.route('/', methods=["OPTIONS", "POST"])
def index():
    if request.method == "OPTIONS":
        # Handle CORS preflight request
        response = jsonify({"message": "CORS preflight request successful"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:8000")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response
    if request.method == "POST":
        form_data = request.get_json()
        print(form_data)

        query_content = f"I want to move to a new city." \
                        f" Here are the things that matter to me:" \
                        f" country: {form_data['country']}," \
                        f" affordability: {form_data['affordability']}," \
                        f" weather: {form_data['weather']}," \
                        f" work-life balance: {form_data['workLifeBalance']}," \
                        f" proximity to nature: {form_data['proximityToNature']}." \
                        f"Where should I go? Make a short answer."
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                       messages=[{"role": "user", "content": query_content}])
        print(chat_completion)
        response = jsonify(message=chat_completion['choices'][0]['message']['content'])
        print(response)
        return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
