from pathlib import Path
from openai import OpenAI
from pymongo import MongoClient
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_on_last_folder(path):
    p = Path(path)
    parent_dir = p.parent
    last_folder = p.name
    return parent_dir, last_folder

def query_documents_without_embeddings(mongo_uri, database_name, directory):
    """
    Query documents from a MongoDB collection that do not have an 'embeddings' field in the 'whole_document'
    dictionary and filter by multiple classname values.
    Parameters:
    - connection_string: str - MongoDB connection URI.
    - database_name: str - Name of the MongoDB database.
    - directory (str): directory to the folder with the lectures
    Returns:
    - list: A list of documents matching the query criteria.
    """
    _, classname = split_on_last_folder(directory)
    client = MongoClient(mongo_uri) # connect to mongo
    db = client[database_name]
    collection = db['embeddings_v2']
    # Define the query
    if classname:
        query = {
            'classname': {'$in': [classname]},
            'whole_document.embeddings': {'$exists': False}
        }
    else:
        query = {'whole_document.embeddings': {'$exists': False}}
    documents = collection.find(query)
    unembedded_lectures = list(documents)
    client.close()
    return unembedded_lectures

def get_embedding(text, model="text-embedding-3-small"):
   '''
   embeds text using openai text-embedding-3-small model
   '''
   client = OpenAI()
   text = text.replace("\n", " ")
   if text == '':
       return []
   else:
       return client.embeddings.create(input = [text], model=model).data[0].embedding
   
def shrink_text_gpt(text,token_reduction_size):
    '''
    this gpt shrinks text document by summarizing the documents to 8191 tokens
    '''
    client = OpenAI()
    system_content = (f"In your input you will receive a long text documents. Your job is to summarize the document in no more than {token_reduction_size}"
                      f" tokens. Give a detailed summary of the text and try to summarize the text close to the {token_reduction_size} limit.")
    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=[
        {"role": "system", "content": system_content},
        {"role": "user", "content": text}
      ],
      max_tokens=token_reduction_size
    )
    return response.choices[0].message.content
 
def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)
    number_of_tokens = len(tokens)
    return number_of_tokens

def shrink_doc_8191(text, embedding_token_limit=8191, openai_api_key=None):
    """
    compresses a document to roughly 8191 tokens to be fed into the OpenAI's embeddings models
    Inputs:
    -text (str): text
    -embedding_token_limit (int): the limit number of tokens an embedding model will accept
    -openai_api_key (str): open i api key
    """
    number_of_tokens = count_tokens(text)
    print("Number of tokens:", number_of_tokens)
    if number_of_tokens > embedding_token_limit:
        chunk_size = 1000
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name="gpt-3.5-turbo",
            chunk_size=chunk_size,
            chunk_overlap=0,
            )
        texts = text_splitter.split_text(text)
        print(f"Split Texts: {texts}")
        reduction_percent = embedding_token_limit / number_of_tokens
        reduced_text = ""
        for chunk in texts:
            token_num = count_tokens(chunk)
            token_reduction_size = token_num * reduction_percent
            reduced_chunk = shrink_text_gpt(chunk, token_reduction_size, openai_api_key=openai_api_key)
            reduced_text += reduced_chunk
            print(f"Original Text:\n{chunk}\n")
            print(f"Summarized Text:\n{reduced_chunk}\n\n")
    return number_of_tokens, reduced_text, texts

def add_embeddings_to_documents(mongo_uri, db_name, documents):
    '''
    embeds text in the documents and updates the database
    '''
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db['embeddings_v2']
    
    openai_text_embedding_limit = 8191
    for document in documents:
        text = document['whole_document']['text']
        if count_tokens(text) > openai_text_embedding_limit:
            text = shrink_text_gpt(text, openai_text_embedding_limit)
        collection.update_one( # update document
            {"_id": document['_id']},
            {"$set": {"whole_document.embeddings": get_embedding(text)}}
        )
    client.close()

def update_documents_with_embeddings(*, mongo_uri, database_name, filepath=None):
    '''
    update documents in the db that don't have embeddings
    Inputs:
    - mongo_uri (str): the connection string for the mongo db
    - database_name (str): name of mongo db
    - classnames (list) - List of classname values to filter the query.
    '''
    documents = query_documents_without_embeddings(mongo_uri, database_name, filepath)
    print(f"Adding embeddings to {len(documents)} documents...")
    add_embeddings_to_documents(mongo_uri, database_name, documents)
    print(f"Documents are embedded!")

