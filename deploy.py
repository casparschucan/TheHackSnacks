#Used to coordinate the backend and the frontend. Serves as entry point in the docker container
from flask_server import server

# Run webserver debug mode
server.run_server()
