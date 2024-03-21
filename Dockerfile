# init python image
FROM python:3.9-slim-bookworm

RUN pip install --upgrade pip
# Set the working directory to /app
WORKDIR /app
# Copy requirements.txt to the working directory
COPY ./requirements.txt /app
# Install the dependencies
RUN pip install -r requirements.txt
# Copy the directory flask_server to /app except the files in .dockerignore
COPY ./ /app
# Make the entrypoint executable
ENTRYPOINT [ "python" ]
# Run the deploy script
CMD ["-u","deploy.py" ]
