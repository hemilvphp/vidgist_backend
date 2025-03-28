
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq

# Set up Groq API key
GROQ_API_KEY = "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"
llm = ChatGroq(model="llama3-8b-8192", temperature = 0, api_key=GROQ_API_KEY)

class TextSummarization:

    def __init__(self):
        self.llm = llm
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    def create_vector_db(self, text):
        """Splits text into chunks and stores in FAISS vector DB."""
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=6000, chunk_overlap=200)
        documents = text_splitter.create_documents([text])
        # Create FAISS vector store
        vector_db = FAISS.from_documents(documents, self.embeddings)
        retriever = vector_db.as_retriever()
        # Retrieve relevant chunks
        retrieved_chunks = retriever.get_relevant_documents(text)
        return retrieved_chunks


    def summarize_chunk(self, chunk):
        """Summarizes a single chunk using Groq API."""
        prompt = f"Summarize this brifly in 10-15 lines:\n\n{chunk}"
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()  # Correctly fetch response content
        except Exception as e:
            print("Error summarizing chunk:", e)
            return ""
        

    def extract_keypoints(self, chunk):
        """Extracts key points from a single chunk using Groq API."""
        prompt = f"""
        Extract key points from the following text and organize them into **clear sections** with **bullet points**.
        - Use concise language, focusing only on **important information**.
        - Ensure a **structured output** with relevant headings and subpoints.
        - Do **not include explanations** about what was removed or modified.
        {chunk}
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()  # Correctly fetch response content
        except Exception as e:
            print("Error extracting key points:", e)
            return ""
        
        
    def summarize_and_extract_keypoints(self, text):
        """Uses RAG to retrieve relevant chunks & summarize."""
        retrieved_chunks = self.create_vector_db(text)
        
        # Summarize each chunk separately
        chunk_summaries = [self.summarize_chunk(chunk.page_content) for chunk in retrieved_chunks]
        # Combine summaries for final summarization
        final_input = " ".join(chunk_summaries)
        final_summary = self.summarize_chunk(final_input)  # Summarizing again for conciseness
        
        
        # Extract key points from each chunk
        keypoints_lists = [self.extract_keypoints(chunk.page_content) for chunk in retrieved_chunks]
        # Combine all key points
        final_keypoints = "\n".join(keypoints_lists)
        return (final_summary, final_keypoints)

    def Summary_and_keypoints(self, large_text):
        return self.summarize_and_extract_keypoints(large_text)
    
text_summarization = TextSummarization()
    
