FROM python:3.10-slim
WORKDIR /app

# Install dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

EXPOSE 8000
# Run the auto-generated app
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]