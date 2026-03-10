# Start from an official Python image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy your requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of your backend code
COPY . .

# Start the FastAPI server
CMD ["uvicorn", "app:medical", "--host", "0.0.0.0", "--port", "8000"]