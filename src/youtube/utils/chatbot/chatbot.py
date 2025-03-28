
import groq
import faiss
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.config import Config

# :small_blue_diamond: Set Up Groq API Key
GROQ_API_KEY = Config.GROQ_API
class Chatbotprocess:

    def __init__(self):
        self.client = groq.Client(api_key=GROQ_API_KEY)
        self.embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # chat_transcript = ''
    # :small_blue_diamond: Step 2: Chunk the Transcript
    # We'll split the transcript into chunks of sentences or paragraphs
    def chunk_transcript(self, transcript: str, chunk_size: int = 500):
        chunks = []
        words = transcript.split()
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i + chunk_size]))
        return chunks

    def faiss_chunks(self, transcript:str):
        chunks = self.chunk_transcript(transcript)
        # :small_blue_diamond: Step 3: Create Vector Store (FAISS)
        # Convert chunks into embeddings
        chunk_embeddings = np.array(self.embedding_model.embed_documents(chunks), dtype="float32")
        # Initialize FAISS
        index = faiss.IndexFlatL2(chunk_embeddings.shape[1])  # L2 distance
        index.add(chunk_embeddings)
        
        return index,self.embedding_model,chunks

    # :small_blue_diamond: Step 4: Retrieval Function
    def retrieve_context(self, user_query:str ,transcript:str):
        """Retrieve the most relevant chunk of transcript based on user query."""
        (index,self.embedding_model,chunks) = self.faiss_chunks(transcript=transcript)
        query_embedding = np.array(self.embedding_model.embed_query(user_query), dtype="float32")
        query_embedding = np.expand_dims(query_embedding, axis=0)  # Reshape for FAISS
        # Search in FAISS
        _, indices = index.search(query_embedding, k=3)  # Retrieve top 3 chunks
        retrieved_text = "\n".join([chunks[i] for i in indices[0]])  # Get matched chunks
        return retrieved_text

    # :small_blue_diamond: Step 5: Chatbot Response with RAG
    def chatbot_response(self,user_input:str,transcript:str):
        """Retrieve relevant context and generate a response using Groq LLM."""
        retrieved_context = self.retrieve_context(user_input,transcript)  # Retrieve relevant transcript context
        if not retrieved_context:
            return "I couldn't find relevant information from the transcript. Could you please ask a different question?"
        # Construct input for LLM
        prompt = f"""
        You are an AI assistant focused on providing accurate, concise answers based on the video transcript provided.
        - **ONLY** answer using the provided transcript context.
        - **DO NOT** generate introductions, greetings, or extra details.
        - **IF the user greets you (e.g., "hello", "hi")**, greet back **only** with "Hello!".
        - **IF the user says "thank you"**, respond with: "You're welcome! let me know if you need any help."
        - **IF the user asks an actual question**, answer using the transcript context.
        Transcript Context:
        {retrieved_context}
        User Question:
        {user_input}
        Respond with only the necessary information. Do not include pleasantries, greetings, or unrelated information.
        """
        # Generate response using Groq API
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Keep responses factual
            max_tokens=200  # Limit response length
        )
        return response.choices[0].message.content.strip()

chatbot_bot = Chatbotprocess()
        





