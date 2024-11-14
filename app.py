import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import PyPDF2
import re
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document

API_KEY = os.environ.get('API_KEY')
OPEN_API_KEY = os.environ.get('OPEN_API_KEY')
print(API_KEY)
print(OPEN_API_KEY)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text
        return extracted_text

# Function to parse user stories from extracted text
def parse_user_stories(text):
    user_stories = {}
    matches = re.findall(r'(User Story \d+:)(.*?)(?=User Story \d+:|$)', text, re.DOTALL)
    for match in matches:
        story_id, story_text = match[0].strip(), match[1].strip()
        user_stories[story_id] = story_text
    return user_stories

# Initialize FAISS VectorStore and load documents
def initialize_faiss(user_stories):
    documents = [Document(page_content=story, metadata={"id": story_id}) for story_id, story in user_stories.items()]  
    embeddings = OpenAIEmbeddings(openai_api_key="OPEN_API_KEY")
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore

# Generate response with RAG (Retrieve and Generate)
def estimate_effort(user_story, vectorstore):
    relevant_docs = vectorstore.similarity_search(user_story, k=3)
    relevant_info = "\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else "No additional context found."

    prompt = (
        f"Estimate the development effort in hours required for the following user story:\n\n"
        f"'{user_story}'\n\n"
        f"Additional Information:\n{relevant_info}\n\n"
        f"Please consider factors like complexity, implementation, and testing."
    )
    response = model.generate_content(prompt)
    return response.text.strip()

# Function to clean the extracted user stories text
def clean_text(text):
    text = re.sub(r'\uf095', '', text)
    text = re.sub(r'-\s+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s([?.!,"])', r'\1', text)
    return text.strip()

# Further refine the cleaned text
def further_clean_text(text):
    text = re.sub(r'\b(\w+)\s*-\s*(\w+)\b', r'\1\2', text)
    text = re.sub(r'3\.\d+.*Requirements.*', '', text)
    text = re.sub(r'4\.\d+.*Requirements.*', '', text)
    text = re.sub(r'5\.\d+.*Requirements.*', '', text)
    return text.strip()

# Generate backend guide for user story
def generate_backend_guide(user_story, vectorstore):
    relevant_docs = vectorstore.similarity_search(user_story, k=3)
    relevant_info = "\n".join([doc.page_content for doc in relevant_docs])

    prompt = (
        f"Provide a detailed guide on how to implement the following user story as a backend service "
        f"using Node.js:\n\n"
        f"User Story: '{user_story}'\n\n"
        f"Additional Context:\n{relevant_info}\n\n"
        f"The guide should include:\n"
        f"- Setting up the Node.js project (e.g., folder structure, dependencies).\n"
        f"- Implementing key service functions (e.g., handling requests, interacting with databases).\n"
        f"- Best practices (e.g., error handling, security, performance optimization).\n"
        f"- Sample code snippets for illustration.\n"
    )

    # Generate the response
    response = model.generate_content(prompt)
    return response.text.strip()

# Flask route to handle PDF file upload and analysis
@app.route('/analyze', methods=['POST'])
def analyze_srs():
    if 'file' not in request.files or 'mode' not in request.form:
        return jsonify({"error": "Please provide a PDF file and mode (estimate/guide)"}), 400

    pdf_file = request.files['file']
    mode = request.form['mode']

    if mode not in ["estimate", "guide"]:
        return jsonify({"error": "Invalid mode. Please choose 'estimate' or 'guide'."}), 400

    # Save the uploaded PDF file
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
    try:
        pdf_file.save(pdf_path)
    except Exception as e:
        return jsonify({"error": f"Could not save file: {str(e)}"}), 500

    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)

    # Parse and clean user stories
    user_stories = parse_user_stories(text)
    cleaned_user_stories = {story_id: clean_text(story_text) for story_id, story_text in user_stories.items()}
    final_user_stories = {story_id: further_clean_text(story_text) for story_id, story_text in cleaned_user_stories.items()}

    # Initialize FAISS vector store
    vectorstore = initialize_faiss(final_user_stories)

    # Generate responses based on the selected mode
    results = {}
    if mode == "estimate":
        for story_id, story_text in final_user_stories.items():
            try:
                results[story_id] = estimate_effort(story_text, vectorstore)
            except Exception as e:
                results[story_id] = f"Error estimating effort: {str(e)}"
    elif mode == "guide":
        for story_id, story_text in final_user_stories.items():
            try:
                results[story_id] = generate_backend_guide(story_text, vectorstore)
            except Exception as e:
                results[story_id] = f"Error generating guide: {str(e)}"

    # Return results as JSON
    return jsonify(results)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
