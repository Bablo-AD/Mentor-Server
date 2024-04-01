from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import chromadb
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from .prompts import context
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer
from .tools import *

# create client and a new collection
chroma_client = chromadb.PersistentClient(path="data/storage/")
try:
    chroma_collection = chroma_client.get_collection("atomichabits")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

except ValueError:
    print("Loading Data..")
    chroma_collection = chroma_client.create_collection("atomichabits")
    documents = SimpleDirectoryReader("data/raw/").load_data()
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

finally:
    print("Loaded Data")

query_engine = index.as_query_engine()



standard_tools = [   
     QueryEngineTool(
         query_engine=query_engine,
         metadata=ToolMetadata(
            name="AtomicHabits",
             description="this gives detailed information about habit forming",
         ),
     ), 
    answer_engine,
    youtube_engine,
    notification_engine,
]


class RAG:
    def __init__(self,userid,chatmemory='',model="gpt-3.5-turbo",context=context,tools=standard_tools,userdata=''):
        if chatmemory == "":
            self.chat_store = SimpleChatStore()
            self.chat_memory = ChatMemoryBuffer.from_defaults(
            chat_store=self.chat_store,
            chat_store_key=userid,
            token_limit=3000,
        )
        else:
            self.chat_store = SimpleChatStore.parse_raw(chatmemory)
            self.chat_memory = ChatMemoryBuffer.from_defaults(chat_store=self.chat_store)
        
        llm = OpenAI(model=model)
        self.load_engines(userdata)
        
        self.agent = ReActAgent.from_tools(tools, llm=llm, verbose=True, context=context,memory=self.chat_memory)
    def load_engines(self,userdata):
        if userdata != '':
            standard_tools.append(user_engine)
        if 'parentmail' in User_var.get():
            
            standard_tools.append(mail_engine)
    def make_query(self,prompt):
        reponse = self.agent.chat(prompt)
        return reponse