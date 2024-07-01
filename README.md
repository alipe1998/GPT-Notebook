# LLM Student Embedded Data

## Overview

**Parsing Lecture Data from Canvas**

The first part of this project involves parsing lecture data from my classes that are stored in the form of pdf, txt, pptx, docx and wav files. Then the text is embedded using the OpenAI embeddings models. The embedded data is then imported to a MongoDB database. 

**MongoDB**

The database has a structure like this:
{class: # this field contains the name of the class that the lecture came from
 title: # this field contains the title of the lecture
 text: # this field contains all the text data
 embedding: [] # This is an array containing the embedded text data
}

**Calling ChatGPT to Answer Questions on the Data**

The second part of the project conntects ChatGPT to the MongoDB to answer specific questions related to the lecture data. A custom API that implemented basic RAG techniques using lecture data was created using fastapi in python. The API was then connected to OpenAI's ChatGPTs custom model as an action. The GPTs model, using the OpenAI API Schema, calls the API to return relevant information from the notes and lectures stored in the database.

## Code

**API Modules**

src/api_app/api_functions/

`main.py` is the main FastAPI app module.

`retrieval.py` contains functions contains functions defined for the basic RAG architecture used in the API.

`test_retrieval.py` contains test functions for the retrieval.py module.

src/api_app/

`docker-compose.yml` docker compose file used to define instructions during deployment.

`Dockerfile` docker code for the container image.

`fly.toml` build file to deploying the app to fly.io PAAS.

`.env` contains api key secrets for local testing and development.

`requirements.txt` requirements file for the app.

`setup.py` specifies where to find packages for local import during development and testing of code.

src/llm_student_v2/

`data_to_mongo.py` contains the functions necessary to extract, transform and load the lectures data from various file types to the MongoDB.

`embeddings.py` contains functions used to embed the text extracted from the lectures and notes.

**Scripts**

`text_to_embeddings_run_v2.py` takes a filepath to a directory containing files as the entry point and extracts all text from the files, embeds the text using OpenAI embedding models and imports them to a MongoDB.

**Data**

data/lectures/

Lectures and notes are further subdivided into folders based on class in this directory.


