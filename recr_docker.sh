sudo docker-compose down
sudo docker image build -t sus-server .
sudo docker-compose up -d
docker logs -f Sus-Server