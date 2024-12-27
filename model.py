from flask import Flask, request, jsonify
import chromadb
import os
import requests
import PyPDF2

app = Flask(__name__)

DB_NAME = "QnA"
client = chromadb.Client()
db = client.get_or_create_collection(name=DB_NAME)

class PDFReader:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def read(self):
        with open(self.pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return [page.extract_text() for page in pdf_reader.pages]

# Initialize FAQ documents if the database is empty
if db.count() == 0:
    pdf_path = "Company_FAQ.pdf"
    pdf_reader = PDFReader(pdf_path)
    pdf_text = pdf_reader.read()
    
    for idx, page in enumerate(pdf_text):
        db.add(documents=[page], ids=[f"page-{idx}"])
    print("FAQ documents added to the database.")

@app.route("/query", methods=["POST"])
def ask_llama():
    data = request.json
    username = data.get("username")
    query = data.get("query")

    if not username or not query:
        return jsonify({"error": "Username and query are required."}), 400

    user_file = f"{username}.txt"

    business_prompt = """
    You are a smart business chatbot named Zola for 'Acme Corporation', here to assist customers with general business inquiries. 
    Your responses should be clear, concise, professional, and based on the FAQ provided below.
    Please respond intelligently, just like a human customer support representative.
    """

    full_prompt = business_prompt + f"\nUser's Query: {query}\nResponse:"

    result = db.query(query_texts=[query], n_results=1)

    if not result["documents"]:
        response_text = "Sorry, I couldn't find an answer. Try rephrasing your question."
    else:
        relevant_passages = result["documents"][0]
        if not relevant_passages:
            response_text = "I cannot understand your question."
        else:
            url = "http://localhost:11434/api/chat"
            model = "llama3.2:latest"
            data = {
                "model": model,
                "messages": [{"role": "user", "content": full_prompt}],
                "stream": False
            }
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, json=data, headers=headers)
            response_data = response.json()
            response_text = response_data.get("message", {}).get("content", "Error: Unexpected response format.")

    with open(user_file, "a") as file:
        file.write(f"Query: {query}\nResponse: {response_text}\n\n")

    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
