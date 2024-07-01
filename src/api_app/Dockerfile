# Use the official Python image from the Docker Hub
FROM python:3.9

# Set the working directory
WORKDIR /api_app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Create the directory for the api_functions package
RUN mkdir -p ./api_functions

# Copy the retrieval module and main.py file to the api_functions directory
COPY api_functions/retrieval.py ./api_functions/
COPY api_functions/main.py ./api_functions/

# Expose the port that the app will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "api_functions.main:app", "--host", "0.0.0.0", "--port", "8000"]