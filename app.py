import sys
import time
import torch
import numpy
from flask import Flask, jsonify, request
from src.helper import download_hugging_face_embeddings
from langchain.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings, ChatNVIDIA
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores import chroma
from langchain.llms import llamacpp
from langchain_openai import AzureOpenAI
from langchain.agents import initialize_agent, load_tools, AgentType
# from openai import AzureOpenAI
from langchain.callbacks.manager import CallbackManager
from dotenv import load_dotenv
from src.prompt import *
from logs.logger import get_logger
from src.llm import LLMOutHandler
import os
# from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

# Initialize logger
logger = get_logger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()
NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY')
AZURE_ENDPOINT = os.environ.get('AZURE_ENDPOINT')
AZURE_API_KEY = os.environ.get('AZURE_API_KEY')
SERP_API_KEY = os.environ.get('SERP_API_KEY')

# Define constants
index_name = "drs_db"

# Download and initialize embeddings
embeddings = download_hugging_face_embeddings()

# Determine device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize LLM Output Handler
llm_custom = LLMOutHandler(device)

# Initialize document search with Chroma
docsearch = chroma.Chroma(persist_directory=index_name, embedding_function=embeddings)

# Initialize prompt template
PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"]) 

# Define chain type keyword arguments
chain_type_kwargs = {"prompt": PROMPT}

'''Code for LlamaCpp model'''
llm=llamacpp.LlamaCpp(model_path=r"model\llama-2-7b-chat.Q5_K_M.gguf.bin",
                      n_ctx=2048, 
                      n_gpu_layers=100,
                      n_batch=512, 
                      n_threads= 1, 
                      model_kwargs={'model_type': 'llama', 
                                    'max_new_tokens':1020, 
                                    'context_length':1020, 
                                    'gpu_layers': 50},
                      temperature=0.1,
                      callback_manager=CallbackManager([llm_custom]),
                      verbose=True,
                      streaming=True)

'''Code for OpenAI LLM GPT-3.5-turbo'''
# llm=openai.OpenAI(openai_api_key=os.environ.get('OPENAI_API_KEY'), model_name="gpt-3.5-turbo", temperature=0.75, callback_manager=CallbackManager([llm_custom]), verbose=True, max_tokens=2048, context_length=2048)

'''Code for NVIDIA Nim LLM'''
# llm=ChatNVIDIA(base_url = "https://integrate.api.nvidia.com/v1", nvidia_api_key=NVIDIA_API_KEY, model='meta/llama3-70b-instruct', max_tokens=1024, temperature=0.1, callback_manager=CallbackManager([llm_custom]), verbose=True, streaming=True)

'''Azure OpenAI langchain Code'''
# llm = AzureOpenAI(azure_endpoint=AZURE_ENDPOINT, model="gpt-3.5-turbo", api_key=AZURE_API_KEY, api_version="2024-12-01", temperature=0.1, callback_manager=CallbackManager([llm_custom]), verbose=True, max_tokens=2048, context_length=2048)

'''Trying to code llm-cpp code from the documentation here'''
# from langchain.callbacks.manager import CallbackManager
# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
# llm2 = llamacpp.LlamaCpp(model_path=r"model/llama-2-7b-chat.ggmlv3.q4_0.bin", n_ctx=4096, n_gpu_layers=-1, n_threads=4, callback_manager=callback_manager, verbose=True, temperature=0.5, context_length=4096, max_tokens=2048)
# llm_chain = LLMChain(llm=llm2, prompt=prompt)
# llm_chain = invoke()
# llama-2-7b-chat.Q5_K_M.gguf
# TheBloke/Llama-2-7B-Chat-GGUF

'''Code for CTransformers/ ggml models'''
# llm=ctransformers.CTransformers(model=r"model/llama-2-7b-chat.ggmlv3.q4_0.bin",
#                   model_type="llama",
#                   config={'max_new_tokens':512,
#                           'temperature':0.7})

# Initialize RetrievalQA chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff", 
    retriever=docsearch.as_retriever(search_kwargs={'k': 5}),
    return_source_documents=False, 
    chain_type_kwargs=chain_type_kwargs,
    verbose=True
)

@app.route("/")
def index():
    """
    Root URL route, simply returns a welcome message.
    """
    return jsonify({"message": "LLM API running for DRS Chatbot "}), 200

@app.route("/get", methods=["POST"])
# @cross_origin()
def chat():
    """
    API endpoint that handles the chat functionality based on user input.
    """
    start = time.time()
    data = request.get_json()
    input_msg = data.get("msg")
    if not input_msg:
        return jsonify({"error": "No input message provided"}), 400

    logger.info(f"Received input: {input_msg}")
    result = qa({"query": input_msg})
    response_msg = result["result"]
    logger.info(f"Response: {response_msg}")
    logger.info(f'Time taken: {round(time.time() - start, 2)} seconds')
    return jsonify({"response": response_msg})

if __name__ == '__main__':
    print('jmd shree ganesha')
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(device)
    print("starting server")
    llm_custom = LLMOutHandler(device)
    app.run(host="0.0.0.0", port=8080, debug=True)
    
    
'''
    {
    "msg": "What services does Digital Rhombus offer?"
    }
    postman api body
'''