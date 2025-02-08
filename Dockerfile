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
CMD ["python3", "-m", "flask", "--app", "src/main.py", "run", "--no-debugger", "--no-reload"]