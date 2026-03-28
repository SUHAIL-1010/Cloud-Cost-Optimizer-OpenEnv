FROM python:3.10-slim
WORKDIR /app

# Look for requirements.txt in the main folder now!
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your environment code
COPY . .

# Expose the specific port Hugging Face requires
EXPOSE 7860

# Run the server on port 7860
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]