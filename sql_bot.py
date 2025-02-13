from langchain_ollama import ChatOllama
from langchain.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
import urllib.parse
import os
from dotenv import find_dotenv, load_dotenv
import uuid
from langsmith import Client
from run_models_utils import run_sql_query

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

model = ChatOllama(model="deepseek-coder:1.3b")

db_password = urllib.parse.quote_plus("Root@1234")
db = SQLDatabase.from_uri(f"mysql+pymysql://root:{db_password}@127.0.0.1:3306/classicmodels")

sql_chain = create_sql_query_chain(model, db)

def run_query(question):
    print("Running SQL Query")
    sql_result = run_sql_query(sql_chain, question)
    print("SQL Query Result:", sql_result)

# test questions
question = "can you share the relation between the tables in the database? And ask me 5 complex SQL queries. By solving them, I will be able to understand the SQL better."

run_query(question)
