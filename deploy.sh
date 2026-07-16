cd /var/www/ariot
docker cp frontend/templates/index.html ariot-api-1:/app/frontend/templates/index.html
docker cp frontend/static/js/main.js ariot-api-1:/app/frontend/static/js/main.js
