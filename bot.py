#pip install streamlit pypdf2 langchain python-dotenv faiss-cpu openai transformers
#pip install -U langchain-community

import streamlit as st
import time
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from htmltemplate import css, bot_template, user_template
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

# Default system message
default_system_message = SystemMessage(content=("You are a helpful assistant. Your knowledge is strictly limited to the uploaded PDFs. "
                                                "If the user asks about something not in the PDFs, politely tell them you can only answer based on the documents. "
                                                "However, if the user greets you (e.g., 'hi', 'hello', 'thank you') or expresses feelings (e.g., 'not satisfied', 'can you elaborate'), respond in a natural and human-like way."))


# Function to extract text from a list of PDF files
def extract_text_from_pdfs(pdf_files):
    full_text = ""
    for pdf_file in pdf_files:
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text
    return full_text

# Function to split text into manageable chunks for processing
def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200):
    splitter = CharacterTextSplitter(separator="\n", chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len)
    chunks = splitter.split_text(text)
    return chunks

# Create a FAISS vector store from text chunks for document retrieval
def create_vectorstore_from_chunks(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# Generate captions for images using a BLIP model
def generate_image_caption(image_file):

    # Process image
    image = Image.open(image_file).convert("RGB")
    inputs = processor(image, return_tensors="pt")

    # Generate a caption
    output = model.generate(**inputs)
    caption = processor.decode(output[0], skip_special_tokens=True)

    return caption

# Initialize Streamlit session state variables
def initialize_session_state():
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "messages" not in st.session_state:
        st.session_state.messages = [default_system_message]
    if "image_data" not in st.session_state:
        st.session_state.image_data = []
    if "chat_summary" not in st.session_state:
        st.session_state.chat_summary = ""
    if "user_avatar" not in st.session_state:
        st.session_state.user_avatar = "😊"
    if "bot_avatar" not in st.session_state:
        st.session_state.bot_avatar = "🤖"


# Process user input and generate responses using the chat model
def process_user_input(user_question, chat_model):
    # Validate user input
    if not user_question.strip():
        st.warning("Please enter a valid question.")
        return
    
    if not st.session_state.vectorstore:
        st.warning("Please upload PDF files to start asking questions.")
        return

    st.session_state.messages.append(HumanMessage(content=user_question))

    retriever = st.session_state.vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(user_question)
    context = "\n".join([doc.page_content for doc in docs])

    if not context.strip():
        bot_response = "I'm sorry, I cannot answer that question as it is outside the scope of the uploaded documents."
        st.session_state.messages.append(AIMessage(content=bot_response))
    else:
        system_prompt = f"\nContext:\n{context}"
        st.session_state.messages.append(SystemMessage(content=system_prompt))

        with st.spinner("Thinking... 🤔"):
            response = chat_model(st.session_state.messages)
            bot_response = response.content.strip()
        st.session_state.messages.append(AIMessage(content=bot_response))

    for msg in st.session_state.messages[1:]:
        if isinstance(msg, HumanMessage):
            st.write(user_template.replace("{{MSG}}", msg.content).replace("😊", st.session_state.user_avatar), unsafe_allow_html=True)
        elif isinstance(msg, AIMessage):
            st.write(bot_template.replace("{{MSG}}", msg.content).replace("🤖", st.session_state.bot_avatar), unsafe_allow_html=True)

# Generate a summary of the chat session
def generate_chat_summary():
    if not st.session_state.messages:
        st.info("No chat history to summarize.")
        return

    with st.spinner("Summarizing chat..."):
        chat_history = "\n".join([msg.content for msg in st.session_state.messages if isinstance(msg, (HumanMessage, AIMessage))])
        summary_prompt = f"Provide a concise summary of the following conversation:\n{chat_history}"
        chat_model = ChatOpenAI(temperature=0)
        summary_response = chat_model([SystemMessage(content=summary_prompt)])
        st.session_state.chat_summary = summary_response.content

    st.success("Summary generated successfully!")

# Interface for the PDF chatbot feature
def pdf_chatbot_interface():
    st.header("PDF Chatbot 🤖")
    st.text("Ask questions based on your uploaded PDFs")

    chat_model = ChatOpenAI(temperature=0)

    # Clear chat history
    if st.button("Clear Chat", key="pdf_clear"):
        st.session_state.messages = [default_system_message]
        st.success("Chat history cleared!")
        time.sleep(1)
        st.rerun()

    # Generate chat summary
    if st.button("Generate Summary", key="generate_summary"):
        generate_chat_summary()
        if st.session_state.chat_summary:
            st.write("### Chat Summary")
            st.write(st.session_state.chat_summary)

    # User input form for submitting questions
    with st.form("chat_form", clear_on_submit=True):
        user_question = st.text_input("Ask a question about your documents:", key="user_input")
        submitted = st.form_submit_button("Send")

    # Process the question when the form is submitted
    if submitted and user_question:
        process_user_input(user_question, chat_model)

# Interface for the image identifier feature
def image_identifier_interface():
    st.header("Image Identifier 🖼️")
    st.text("Upload images to get captions")

    # Display uploaded images and their captions
    if st.session_state.image_data:
        for idx, image_data in enumerate(st.session_state.image_data):
            st.image(image_data['image'], caption=f"Image {idx + 1}: {image_data['caption']}")
    else:
        st.info("No images uploaded yet. Please upload images in the sidebar.")

# Sidebar for file management and settings
def sidebar_interface():
    st.sidebar.title("File Management 📂")
    
    with st.sidebar:
        with st.expander("Upload Files", expanded=True):
            pdf_files = st.file_uploader("Upload your PDFs", accept_multiple_files=True, type=["pdf"])
            image_files = st.file_uploader("Upload Images", accept_multiple_files=True, type=["png", "jpg", "jpeg"])
            
            if st.button("Process Files", key="process_files"):
                if pdf_files:
                    with st.spinner("Processing PDFs... ✨"):
                        pdf_text = extract_text_from_pdfs(pdf_files)
                        text_chunks = split_text_into_chunks(pdf_text)
                        st.session_state.vectorstore = create_vectorstore_from_chunks(text_chunks)
                    st.success("PDFs processed successfully! 🎉")
                if image_files:
                    with st.spinner("Processing Images... 🖼️"):
                        st.session_state.image_data = []
                        for image_file in image_files:
                            caption = generate_image_caption(image_file)
                            st.session_state.image_data.append({"image": image_file, "caption": caption})
                    st.success("Images processed successfully! 🎉")

# Main function
def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with PDFs and Images", layout="wide")
    st.write(css, unsafe_allow_html=True)

    # Initialize session state variables
    initialize_session_state()
    sidebar_interface()
    
    st.title("PDF Chatbot and Image Identifier")
    st.text("Welcome to the PDF Chatbot and Image Identifier! Use the tabs below to navigate between the chatbot and image identifier features.")
    
    # Tabs for PDF chatbot and image identifier
    tabs = st.tabs(["PDF Chatbot", "Image Identifier"])

    with tabs[0]:
        pdf_chatbot_interface()

    with tabs[1]:
        image_identifier_interface()

if __name__ == "__main__":
    main()