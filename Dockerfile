# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the contents of the local app directory to the container
COPY ./app /app

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8050

RUN pip install gunicorn

# Command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:8050", "main:server"]
