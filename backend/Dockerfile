FROM python:3.12-slim
FROM mcr.microsoft.com/playwright/python:v1.52.0-noble
# Set work directory
WORKDIR /app

# Update pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements file
COPY ./requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Cài đặt browsers cho Playwright
RUN playwright install

# Copy application source code
COPY ./src /app/src

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
