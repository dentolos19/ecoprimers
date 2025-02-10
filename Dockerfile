FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--conf", "src/gunicorn.py", "--chdir", "src", "--bind", "0.0.0.0:5000", "main:app"]