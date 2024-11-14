import google.generativeai as genai
import PyPDF2
import re
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document


genai.configure(api_key="xxxxxxx")

model = genai.GenerativeModel('gemini-pro')

# extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text
        return extracted_text

# Parse user stories from the extracted text
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
    embeddings = OpenAIEmbeddings(openai_api_key="xxxxxxxxx")
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore

# Generate response with RAG
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

# function to analyze the SRS document
def analyze_srs(file_path, mode="estimate"):
    if mode not in ["estimate", "guide"]:
        raise ValueError("Invalid mode. Choose either 'estimate' or 'guide'.")
    # Step 1: Extract text from PDF
    text = extract_text_from_pdf(file_path)

    # Step 2: Parse user stories
    user_stories = parse_user_stories(text)

    # Step 3: Clean and refine each user story description
    cleaned_user_stories = {story_id: clean_text(story_text) for story_id, story_text in user_stories.items()}
    final_user_stories = {story_id: further_clean_text(story_text) for story_id, story_text in cleaned_user_stories.items()}

    # Step 4: Initialize FAISS vector store
    vectorstore = initialize_faiss(final_user_stories)

    # Step 5: Process user stories based on the chosen mode
    if mode == "estimate":
       
        effort_estimations = {}
        for story_id, story_text in final_user_stories.items():
            try:
                effort_estimations[story_id] = estimate_effort(story_text, vectorstore)
            except Exception as e:
                effort_estimations[story_id] = f"Error estimating effort: {e}"

        for story_id, estimation in effort_estimations.items():
            print(f"{story_id}: Estimated Effort - {estimation}")
    
    elif mode == "guide":
        backend_guides = {}
        for story_id, story_text in final_user_stories.items():
            try:
                backend_guides[story_id] = generate_backend_guide(story_text, vectorstore)
            except Exception as e:
                backend_guides[story_id] = f"Error generating backend guide: {e}"

        for story_id, guide in backend_guides.items():
            print(f"{story_id}: Backend Service Guide - {guide}")
    else:
        print("Invalid mode. Please choose either 'estimate' or 'guide'.")

file_path = "./srs.pdf"
mode = "estimate"  # or "guide"
analyze_srs(file_path, mode)

