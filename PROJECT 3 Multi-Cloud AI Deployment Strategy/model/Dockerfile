# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
# Since we only have main.py for now, we'll install dependencies directly
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV CLOUD_PROVIDER=Local

# Run main.py when the container launches
CMD ["python", "main.py"]
