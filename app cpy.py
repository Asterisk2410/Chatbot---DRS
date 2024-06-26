import sys , time, torch, numpy
from flask import Flask, render_template, jsonify, request
from src.helper import download_hugging_face_embeddings
from langchain.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores import chroma
from langchain.llms import ctransformers, llamacpp, openai, huggingface_hub
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings, ChatNVIDIA
from langchain.callbacks.manager import CallbackManager
from dotenv.main import load_dotenv
from src.prompt import prompt_template
from logs.logger import get_logger
import torch
from src.llm import LLMOutHandler
import os


logger = get_logger(__name__)
app = Flask(__name__)

load_dotenv()
NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
index_name = "drs_db"
embeddings = download_hugging_face_embeddings()

device = "cuda" if torch.cuda.is_available() else "cpu"

llm_custom = LLMOutHandler(device)

docsearch = chroma.Chroma(persist_directory=index_name, embedding_function=embeddings)

#prompt_template from src/prompt.py
PROMPT=PromptTemplate(template=prompt_template, input_variables=["context", "question"]) 

chain_type_kwargs={"prompt": PROMPT}

'''Code for LlamaCpp model'''
# llm=llamacpp.LlamaCpp(model_path=r"model\llama-2-7b-chat.Q5_K_M.gguf.bin",
#                       n_ctx=2048, 
#                       n_gpu_layers=100,
#                       n_batch=512, 
#                       n_threads= 1, 
#                       model_kwargs={'model_type': 'llama', 
#                                     'max_new_tokens':1020, 
#                                     'context_length':1020, 
#                                     'gpu_layers': 50},
#                       temperature=0.1,
#                       callback_manager=CallbackManager([llm_custom]),
#                       verbose=True,
#                       streaming=True)

'''Code for OpenAI LLM GPT-3.5-turbo'''
# llm=openai.OpenAI(openai_api_key=os.environ.get('OPENAI_API_KEY'), model_name="gpt-3.5-turbo", temperature=0.75, callback_manager=CallbackManager([llm_custom]), verbose=True, max_tokens=2048, context_length=2048)

'''Code for NVIDIA Nim LLM'''
llm=ChatNVIDIA(base_url = "https://integrate.api.nvidia.com/v1", nvidia_api_key=NVIDIA_API_KEY, model='meta/llama3-70b-instruct', max_tokens=1024, temperature=0.7, callback_manager=CallbackManager([llm_custom]), verbose=True, streaming=True)

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
print(llm)
qa=RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=docsearch.as_retriever(search_kwargs={'k': 5}),
    return_source_documents=False, 
    chain_type_kwargs=chain_type_kwargs,
    verbose=True)

@app.route("/")
def index():
    """
    Route decorator for the root URL ("/") that defines a function named "index".
    This function returns the rendered template "chat.html".
    """
    return render_template('head.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    """
    A function that handles the chat functionality based on user input, performs a query, and returns the response.
    """
    start = time.time()
    msg = request.form["msg"]
    input = msg
    print(input)
    result=qa({"query": input})
    print("Response : ", result["result"])
    print('time taken ', round(time.time() - start,2), 'seconds')
    return str(result["result"])

if __name__ == '__main__':
    print('jmd shree ganesha')
    print(llm)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(device)
    print("starting server")
    llm_custom = LLMOutHandler(device)
    app.run(host="0.0.0.0", port= 8080, debug=True)
    