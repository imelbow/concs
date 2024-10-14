FROM python:3.12-slim

WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app directory
COPY app/ ./app/

# Copy config file
COPY config.yaml .

# Set the working directory to the app folder
WORKDIR /app/app

# Run the application
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]