from flask import Flask, render_template,request,jsonify
import openai
import os
from dotenv import load_dotenv 

load_dotenv() 


app = Flask(__name__)

api_key = os.getenv("key")

client = openai.Client(api_key=api_key)

def get_response(prompt):
    stm = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    res=stm.choices[0].message.content
    return res


app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/process_text', methods=['POST'])
def process_text():
    data = request.get_json()
    text = data['text']
    print(text)
    
    processed_text = text.lower()
    
    response = get_response(processed_text)
    print(response)
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True,port=8080) 