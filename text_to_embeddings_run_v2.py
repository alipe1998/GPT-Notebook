import os
import src.llm_student_v2.data_to_mongo as dm
import src.llm_student_v2.embeddings as embeddings

mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")

def run():
    print('Lecture Data in filepaths should be structured like this for the embedding tool to work the best:\n'
          '└── data\n'
          '    └── [class_name]\n'
          '        └── file1.txt\n'
          '            file2.pdf\n'
          '            file3.wav\n')
    mongo_db = input('Input name of Mongo database: ')
    while True:
        filepath = input('Input path to folder containing all text data: ')
        try:
            dm.import_lectures(filepath, mongodb_name=mongo_db, 
                               mongo_uri=mongo_connection_string)
        except Exception as e:
            print(f'Failed to import lectures. Error: {e}')
        try:
            embeddings.update_documents_with_embeddings(mongo_uri=mongo_connection_string,
                                                        database_name=mongo_db,
                                                        filepath=filepath)
        except Exception as e:
            print(f"Failed to embed the lectures from {filepath}.\nError: {e}")
        # Ask if the user wants to continue or not
        while True:
            more_lectures = input('Would you like to import more lectures? y/[n]: ').lower().strip()
            if more_lectures == 'y':
                break  # Breaks the inner loop and continues the outer loop
            else:
                print("Exiting the program.")
                exit() # Exits the program directly

run()