import streamlit as st
import os
import logging
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
import ollama
import tempfile
import datetime

# Import authentication module
from auth import (
    initialize_oauth_component,
    check_authentication,
    get_user_info_from_token,
    display_user_info,
    logout
)


# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
DOC_PATH = "./data/jpr1700-1ch10-2.pdf"
MODEL_NAME = "mistral"
EMBEDDING_MODEL = "nomic-embed-text"
VECTOR_STORE_NAME = "simple-rag"
PERSIST_DIRECTORY = "./chroma_db"


def ingest_pdf(doc_path):
    """Load PDF documents."""
    if os.path.exists(doc_path):
        loader = UnstructuredPDFLoader(file_path=doc_path)
        data = loader.load()
        logging.info("PDF loaded successfully.")
        return data
    else:
        logging.error(f"PDF file not found at path: {doc_path}")
        st.error("PDF file not found.")
        return None


def split_documents(documents):
    """Split documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
    chunks = text_splitter.split_documents(documents)
    logging.info("Documents split into chunks.")
    return chunks


@st.cache_resource
def load_vector_db():
    """Load or create the vector database."""
    # Pull the embedding model if not already available.
    ollama.pull(EMBEDDING_MODEL)

    embedding = OllamaEmbeddings(model=EMBEDDING_MODEL)

    if os.path.exists(PERSIST_DIRECTORY):
        vector_db = Chroma(
            embedding_function=embedding,
            collection_name=VECTOR_STORE_NAME,
            persist_directory=PERSIST_DIRECTORY,
        )
        logging.info("Loaded existing vector database.")
    else:
        # Load and process the PDF document
        data = ingest_pdf(DOC_PATH)
        if data is None:
            return None

        # Split the documents into chunks
        chunks = split_documents(data)

        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding,
            collection_name=VECTOR_STORE_NAME,
            persist_directory=PERSIST_DIRECTORY,
        )
        vector_db.persist()
        logging.info("Vector database created and persisted.")
    return vector_db


def create_retriever(vector_db, llm):
    """Create a multi-query retriever."""
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assisstant.  Your task is to generate five different versions of the given user question to retrieve relevant documents from a vector database. By generating multiple perspectives on the user question, your goal is to help the user overcome some of the limitations of the distance-based similarity search. Provide these alternative questions seperated by newlines.
        Original question: {question}""",
    )

    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(), llm, prompt=QUERY_PROMPT
    )
    logging.info("Retriever created.")
    return retriever


def create_chain(retriever, llm):
    """Cretae the chain with preserved syntax."""
    # RAG prompt
    template = """Answer the question based ONLY on the following context:
{context}
Question: {question}
"""

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    logging.info("Chain cretaed with preserved syntax.")
    return chain


def show_login_page():
    """Display the login page with NASA Launchpad authentication."""
    st.set_page_config(
        page_title="SAGE - Login",
        page_icon="ðŸš€",
    )

    st.image("./images/NasaControlRoom.jpg", width=800)
    st.markdown("<h1 style='text-align: center;'>SAGE<br><span style='font-size: 0.8em;'>Safety Analysis Generation Engine</span></h1>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Welcome to SAGE")
    st.markdown("Please authenticate with NASA Launchpad to access the application.")

    # Initialize OAuth component
    oauth2 = initialize_oauth_component()

    # Get OAuth configuration from secrets
    redirect_uri = st.secrets["oauth"]["redirect_uri"]
    scopes = st.secrets["oauth"]["scopes"]

    # Create the authorize button
    result = oauth2.authorize_button(
        name="Login with NASA Launchpad",
        redirect_uri=redirect_uri,
        scope=scopes,
        key="nasa_login",
        use_container_width=True,
        height=600,
        width=800,
    )

    # Handle the OAuth callback
    if result and 'token' in result:
        logging.info("OAuth callback received")
        logging.info(f"Token keys: {result['token'].keys() if result['token'] else 'None'}")

        # Store the token in session state
        st.session_state.token = result['token']

        # Extract access token
        access_token = result['token'].get('access_token')
        if access_token:
            st.session_state.access_token = access_token
            logging.info("Access token extracted successfully")

        # Extract user information (tries userinfo endpoint, then id_token)
        try:
            user_info = get_user_info_from_token(result['token'])
            if user_info:
                st.session_state.user_info = user_info
                # Log user identifier
                user_identifier = user_info.get('email') or user_info.get('name') or user_info.get('preferred_username') or user_info.get('sub', 'Unknown')
                logging.info(f"User logged in: {user_identifier}")
                st.success("Authentication successful! Redirecting...")
            else:
                logging.warning("Failed to extract user information")
                st.warning("⚠️ Authentication succeeded but failed to retrieve user information. Redirecting anyway...")
        except Exception as e:
            logging.error(f"Error extracting user info: {str(e)}")
            st.error(f"Error extracting user information: {str(e)}")

        st.rerun()
    elif result:
        logging.warning(f"OAuth callback received but no token. Result keys: {result.keys()}")
        st.error(f"Authentication failed: No token in response. Keys: {list(result.keys())}")

    st.markdown("---")
    st.markdown(f"<div style='text-align: center;'><p style='font-family: -apple-system, BlinkMacSystemFont;'>A specialized tool for generating safety analysis documentation<br>Developed by JSC EC4<br>Date: {datetime.date.today()}</p></div>", unsafe_allow_html=True)


def show_sage_app():
    """Display the main SAGE application (authenticated users only)."""
    st.image("./images/NasaControlRoom.jpg", width=800)
    st.markdown("<h1 style='text-align: center;'>SAGE<br><span style='font-size: 0.8em;'>Safety Analysis Generation Engine</span></h1>", unsafe_allow_html=True)

    # Debug panel (temporary - remove in production)
    with st.expander("🔍 Debug: Session State", expanded=False):
        st.write("**Token exists:**", 'token' in st.session_state)
        st.write("**Access token exists:**", 'access_token' in st.session_state)
        st.write("**User info exists:**", 'user_info' in st.session_state)

        if 'token' in st.session_state:
            st.write("**Token keys:**", list(st.session_state.token.keys()) if st.session_state.token else "None")

        if 'user_info' in st.session_state:
            st.write("**User info:**", st.session_state.user_info)
        else:
            st.warning("⚠️ User info not loaded - get_user_info() may have failed")

    # Display user info in sidebar
    display_user_info()

    # User input
    user_input = st.text_area(
        "",
        placeholder="Ask me anything about safety analysis documentation...",
        label_visibility="collapsed",
        height=120
    )

    if user_input:
        with st.spinner("Generating response..."):
            try:
                # Initialize the language model
                llm = ChatOllama(model=MODEL_NAME)

                # Load the vector database
                vector_db = load_vector_db()
                if vector_db is None:
                    st.error("Failed to load or create the vector database.")
                    return
                # Create the retriever
                retriever = create_retriever(vector_db, llm)

                # Create the chain
                chain = create_chain(retriever, llm)

                # Get the response
                response = chain.invoke(input=user_input)

                st.markdown("**Assistant:**")
                st.write(response)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please enter a question to get started.", icon=":material/help:")

    st.markdown(f"<div style='text-align: center;'><p style='font-family: -apple-system, BlinkMacSystemFont;'>A specialized tool for generating safety analysis documentation<br>Developed by JSC EC4<br>Date: {datetime.date.today()}</p></div>", unsafe_allow_html=True)


def main():
    """Main application entry point with authentication."""
    st.set_page_config(
        page_title="SAGE",
        page_icon="ðŸš€",
    )

    # Check authentication status
    if check_authentication():
        # User is authenticated, show the main app
        show_sage_app()
    else:
        # User is not authenticated, show login page
        show_login_page()


if __name__ == "__main__":
    main()