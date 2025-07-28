# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script
COPY 1_b.py ./

# Copy sample pdfs and rename to 'pdfs' as expected by the script
COPY "sample pdfs" ./pdfs

# Set the default command to run the script
CMD ["python", "1_b.py"] 