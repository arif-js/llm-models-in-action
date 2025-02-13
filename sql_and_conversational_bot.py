from langchain_ollama import ChatOllama
from langchain.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
import urllib.parse
import os
from dotenv import find_dotenv, load_dotenv
import uuid
from langsmith import Client
from run_models_utils import run_sql_query, run_conversational_tool

load_dotenv(find_dotenv())
os.environ["LANGCHAIN_API_KEY"] = str(os.getenv("LANGCHAIN_API_KEY"))
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

# Create id
uid = uuid.uuid4()
# Create a client
client = Client()
# Create a unique name
PROJECT_NAME = "mysql-query-langchain-ollama" + str(uid)
# Create the project
session = client.create_project(
    project_name=PROJECT_NAME,
    description="mysql custom agent",
)

model = ChatOllama(model="llama3.2:latest")

db_password = urllib.parse.quote_plus("Root@1234")
db = SQLDatabase.from_uri(f"mysql+pymysql://root:{db_password}@127.0.0.1:3306/classicmodels")

sql_chain = create_sql_query_chain(model, db)

def determine_and_run_query(question):
    # Use the LLM to determine the type of query
    classification_prompt = f"""
    You are an AI assistant that classifies questions based on their intent. 
    Your task is to determine whether a given question is related to a SQL database or is a general conversation.

    If the question requires fetching data or knowing about data from a database, only respond with:
    "SQL Query"

    If the question is a general conversational topic, only respond with:
    "Conversational Query"

    Here is the user's question:
    "{question}"
    """
    response = model.invoke(classification_prompt).content.strip()
    print("Classification Result:", response)
    if response == "SQL Query":
        print("Running SQL Query")
        sql_result = run_sql_query(sql_chain, question)
        print("SQL Query Result:", sql_result)
    elif response == "Conversational Query":
        print("Running Conversational Query")
        conversation_result = run_conversational_tool(model, question)
        print("Conversation Result:", conversation_result)
    else:
        print("Unknown classification:", response)

# test questions
question = "how many customers are there?"

determine_and_run_query(question)
