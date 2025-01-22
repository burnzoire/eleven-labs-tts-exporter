# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install pipenv && pipenv install --system --deploy

# Make port 80 available to the world outside this container
EXPOSE 80

# Run generate.py when the container launches
ENTRYPOINT ["python", "generate.py"]
