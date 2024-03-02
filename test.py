
from dotenv import load_dotenv
load_dotenv()
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from IPython.display import Markdown, display
import chromadb
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from prompts import context
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer
#from llama_hub.youtube_transcript import YoutubeTranscriptReader
# create client and a new collection
chroma_client = chromadb.PersistentClient(path="./data/storage/")
chroma_collection = chroma_client.create_collection("atomichabits")
#youtube_collection = chroma_client.create_collection("syoutube")

# load documents
documents = SimpleDirectoryReader("./data/").load_data()
# set up ChromaVectorStore and load in data
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
#youtube_store = ChromaVectorStore(chroma_collection=youtube_collection)
chat_store = SimpleChatStore()

chat_memory = ChatMemoryBuffer.from_defaults(
    token_limit=3000,
    chat_store=chat_store,
    chat_store_key="user1",
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
#yt_storage_context = StorageContext.from_defaults(vector_store=chat_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)


# Query Data
query_engine = index.as_query_engine()
#response = queryS_engine.query("What is lk99?")
#display(Markdown(f"<b>{response}</b>"))
#print(response)

tools = [
    
    QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="AtomicHabits",
            description="this gives detailed information about habit forming",
        ),
    ),
]
llm = OpenAI(model="gpt-3.5-turbo-0613")
agent = ReActAgent.from_tools(tools, llm=llm, verbose=True, context=context,memory=chat_memory)

while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    result = agent.query(prompt)
    print(result)
