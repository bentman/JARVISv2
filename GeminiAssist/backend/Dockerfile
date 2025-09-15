# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies, including LangChain and a simple web framework like Flask or FastAPI
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY . .

# Expose the port the backend will run on
EXPOSE 5000

# Command to run the backend service
CMD ["python", "app.py"]