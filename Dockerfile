# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Ensure ffmpeg is in the PATH
ENV PATH="/usr/bin/ffmpeg:${PATH}"

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install pipenv && pipenv install --system --deploy

# Make port 80 available to the world outside this container
EXPOSE 80

# Run generate.py when the container launches
CMD ["python", "generate.py"]
