docker-compose up -d db redis
docker-compose build django
docker-compose up -d django

docker-compose exec -T django python manage.py migrate
docker-compose exec -T django python createadmin.py
