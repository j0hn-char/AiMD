# Start from an official Python image
FROM python:3.11

# Install DejaVu fonts required by reportlab
RUN apt-get update && apt-get install -y fonts-dejavu-core && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy your requirements file and install dependencies
COPY requirements.txt .
RUN pip install --timeout=120 --retries=5 -r requirements.txt

# Copy the rest of your backend code
COPY . .

# Start the FastAPI server
CMD ["uvicorn", "app:medical", "--host", "0.0.0.0", "--port", "8000"]