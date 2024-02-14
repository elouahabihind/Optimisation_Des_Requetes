from flask import Flask , render_template, request, jsonify
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

client = OpenAI(
  api_key=os.getenv("GPT_SK"),
)

intstructions_string_few_shot = """hello"""
# intstructions_string_few_shot = """hello everybody this is just a test"""

def query_optimisation(original_query):
    response = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0613:personal::8s8nIXrV",
        messages=[
        {"role": "system", "content": intstructions_string_few_shot},
        {"role": "user", "content": original_query}
        ]
    )
    optimised_query = dict(response)['choices'][0].message.content
    return optimised_query



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    # Get the original query from the POST request
    data = request.get_json()
    original_query = data.get('originalQuery')

    # Call the query_optimisation function
    optimized_query = query_optimisation(original_query)
    
    # Return the optimized query as JSON
    return jsonify({'optimizedQuery': optimized_query})

if __name__ == '__main__':
    app.run(debug=True)
