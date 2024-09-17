FROM python:3.9

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Debugging steps
RUN pip list
RUN pip show google-cloud-documentai
RUN python -c "import sys; print(sys.path)"
RUN find /usr/local/lib/python3.9/site-packages/google -name '*.py' | grep documentai

# Copy the current directory contents into the container at /app
COPY . .
COPY .env .

# Make port 5051 available to the world outside this container
EXPOSE 5051

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5051"]