from flask import Flask, request, jsonify
import google.generativeai as genai
import PyPDF2
import re
import os

API_KEY = os.environ.get('API_KEY')
print(API_KEY)
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Function to extract text from a PDF document
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

# Function to generate either an effort estimate or Node.js implementation guide
def generate_response(user_story, mode="estimate"):
    if mode == "estimate":
        prompt = f"Estimate the development effort in hours required for the following user story:\n\n{user_story}"
    elif mode == "guide":
        prompt = f"""
        Provide a detailed guide on how to implement the following user story as a backend service using Node.js:

        User Story: '{user_story}'

        Include specific instructions on:
        1. Necessary route endpoints and HTTP methods.
        2. Sample code snippets for Express routes and middleware.
        3. Recommended data schema using MongoDB and Mongoose.
        4. Steps for user authentication or authorization if required.
        5. Any other relevant backend logic.
        """
    else:
        raise ValueError("Mode should be either 'estimate' or 'guide'")

    response = model.generate_content(prompt)
    return response.text.strip()

# Clean up the extracted text
def clean_text(text):
    text = re.sub(r'\uf095', '', text)
    text = re.sub(r'-\s+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s([?.!,"])', r'\1', text)
    return text.strip()

# Further cleaning for extraneous sections
def further_clean_text(text):
    text = re.sub(r'\b(\w+)\s*-\s*(\w+)\b', r'\1\2', text)
    text = re.sub(r'3\.\d+.*Requirements.*', '', text)
    text = re.sub(r'4\.\d+.*Requirements.*', '', text)
    text = re.sub(r'5\.\d+.*Requirements.*', '', text)
    return text.strip()

@app.route('/')
def hello():
    return "Hello World!"

# Route to handle PDF file upload and analysis
@app.route('/analyze', methods=['POST'])
def analyze_srs():
    if 'file' not in request.files or 'mode' not in request.form:
        return jsonify({"error": "Please provide a PDF file and mode (estimate/guide)"}), 400

    pdf_file = request.files['file']
    mode = request.form['mode']

    # Save the uploaded PDF to process
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename) 
    pdf_file.save(pdf_path)

    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)

    # Parse and clean user stories
    user_stories = parse_user_stories(text)
    cleaned_user_stories = {story_id: clean_text(story_text) for story_id, story_text in user_stories.items()}
    final_user_stories = {story_id: further_clean_text(story_text) for story_id, story_text in cleaned_user_stories.items()}

    # Generate responses for each user story
    results = {}
    for story_id, story_text in final_user_stories.items():
        response = generate_response(story_text, mode=mode)
        results[story_id] = response

    # Return results as JSON
    return jsonify(results)

# Run the Flask app
if __name__ == '__main__':
    port = os.environ.get('FLASK_PORT') or 8080
    port = int(port)

    app.run(port=port,host='0.0.0.0')
