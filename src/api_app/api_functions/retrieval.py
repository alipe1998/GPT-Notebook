# Contains functions to retrieve the most similar documents from a mongo db
from openai import OpenAI
from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import tiktoken

# counts tokens
def count_tokens(text):
    """
    Counts the number of tokens in a text chunk for the gpt-3.5-turbo model.
    Parameters:
    - text (str): The text chunk to be tokenized.
    Returns:
    - number_of_tokens (int): The number of tokens in the text.
    """
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo") # get the encoding for the specified model
    return len(encoding.encode(text)) # encode the text and count the tokens

# embed user input
def embed_query(query, openai_api_key=None, model="text-embedding-3-small"):
    """
    Embed text using a specified model (default is text-embedding-3-small).
   
    Parameters:
    - text (str): String of text.
    - model (str): OpenAI embedding model (default is text-embedding-3-large).
    - openai_api_key (str): OpenAI API key.
   
    Returns:
    - embeddings (array): Length of embeddings array depends on the model used.
    """
    client = OpenAI(api_key=openai_api_key)
    query = query.replace("\n", " ")
    if count_tokens(query) > 8191:
        print(f"user input is over 8191 and must be shortened to embed")
    else:
        return client.embeddings.create(input=[query], model=model).data[0].embedding

# get data from mongo and perform necessary filters
def get_filtered_data(*, mongo_uri, db_name, collection_name, classname=None):
    """
    Retrieve and filter data from MongoDB.
    Parameters:
    - mongo_uri (str): MongoDB connection string.
    - db_name (str): Name of the database.
    - collection_name (str): Name of the collection.
    Returns:
    - list: filtered pandas DataFrame
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    if classname: # build filter
        filters = {'classname': classname}
    else:
        filters = {}

    documents = collection.find(filters) # Perform the query
    if documents:
        result = list(documents) # Convert the result to a list
        df = pd.DataFrame(result)
        df['embeddings'] = df['whole_document'].apply(lambda x: x.get('embeddings', []))
        return df
    else:
        print('No documents in database to match query')
        return pd.DataFrame

# perform similarity search and return most similar document
def find_most_similar_document(embedding, df, n=1):
    """
    Find the most similar document based on cosine similarity.
 
    Parameters:
    - embedding (array): The embedding array of the query document.
    - df (pd.DataFrame): DataFrame with the data
 
    Returns:
    - dict: The most similar document with its '_id' and 'embeddings'.
    """

    df['embeddings'] = df['embeddings'].apply(np.array) # ensure embeddings in df are in the correct format
    embeddings_matrix = np.stack(df['embeddings'].values) # stack embeddings in the df for cosine sim equation
    similarities = cosine_similarity([embedding], embeddings_matrix)[0] # compute cosine similarity
    top_n_indices = np.argsort(similarities)[-n:][::-1] # get indices of most similar docs
    top_n_similar_docs = df.iloc[top_n_indices] # get most similar docs from df
    top_n_similar_docs = top_n_similar_docs.drop('embeddings', axis=1)
    return top_n_similar_docs.to_dict('records')