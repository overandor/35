# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Make the start.sh script executable
RUN chmod +x start.sh

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the start.sh script when the container launches
CMD ["./start.sh"]
