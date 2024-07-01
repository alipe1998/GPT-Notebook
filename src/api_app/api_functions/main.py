import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from api_functions.retrieval import embed_query, get_filtered_data, find_most_similar_document
from dotenv import load_dotenv

load_dotenv()

# load mongo connection string and api key from env file
mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
API_KEY = os.getenv("API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# define the api key header
api_key_header = APIKeyHeader(name="API-KEY")

class WholeDocument(BaseModel):
    text: str

class Document(BaseModel):
    id: str = Field(alias='_id')
    classname: str
    title: str
    whole_document: WholeDocument

    class Config:
        arbitrary_types_allowed = True

app = FastAPI()

client = MongoClient(mongo_connection_string)
db = client['student_ai']
collection = db['embeddings_v2']

# Dependency to verify API key
def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate API key")

@app.get("/lectures/", response_model=List[Document], dependencies=[Depends(verify_api_key)])
async def find_similar_documents(query: str, classname: Optional[str] = None, n: Optional[int] = 1):
    try:
        embedded_query = embed_query(query, openai_api_key=openai_api_key, model='text-embedding-3-small')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'mongo_string: {mongo_connection_string}\nThere was a problem embedding the user query: {e}')
    try:
        df = get_filtered_data(mongo_uri=mongo_connection_string, db_name='student_ai',
                                          collection_name='embeddings_v2', classname=classname)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'There was a problem filtering the data from MongoDB: {e}')
    if not df.empty:
        try:
            similar_documents = find_most_similar_document(embedded_query, df, n=n)
            # Convert ObjectId to string
            for doc in similar_documents:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            return similar_documents
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'There was a problem calculating the similarity between documents and user query: {e}')
    else:
        raise HTTPException(status_code=204, detail="No Content")
