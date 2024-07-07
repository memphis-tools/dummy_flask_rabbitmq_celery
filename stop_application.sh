#!/bin/bash

CYAN='\033[1;36m'
GREEN='\033[1;32m'
RED='\033[1;31m'
YELLOW='\033[1;33m'
WHITE='\033[1;97m'
RESET='\033[0m'

echo -e "$GREEN[+] Removing swarm stack $RESET"
docker stack rm dummy_flask_rabbitmq_celery &> /dev/null
sleep 2
echo -e "$GREEN[+] Swarm stack removed $RESET"
