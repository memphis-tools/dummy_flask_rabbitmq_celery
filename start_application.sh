#!/bin/bash

# start_application
# This script is dedicated to start a dummy swarm application.
# This is a dummy proof of concept application.
# It illustrates a dummy Flask usage with an asynchronous Celery's task execution.
# Task consists of sending an email with a PDF file attached.
# This script will engage either the docker-compose or the test_docker-compose based on parameters.
# Also script allows to rebuild docker images.

set -e

usage () {
  # User can set a 'test' context and/or ask for rebuild specific images
	echo "[USAGE] $0 [-c|--context] test [-r|--rebuild] nginx|mongo|flask|redis|celery_worker"
}

if [[ -f .env.rc ]]
then
	source .env.rc
fi
TEST_CONTEXT="FALSE"
RUNNING_ENV="prod"
SWARM_NETWORK_NAME="dummy-network"
HOST_NETWORK_NAME="host"
ERLANG_COOKIE_NAME="erlang_cookie"
NGINX_CERTS_FOLDER="nginx/certs"
DOCKER_COMPOSE_FILE_PATH="./docker-compose.yml"
USER_USED_ARGS="FALSE"
CYAN='\033[1;36m'
GREEN='\033[1;32m'
RED='\033[1;31m'
YELLOW='\033[1;33m'
WHITE='\033[1;97m'
RESET='\033[0m'
DOCKER_IMAGE_NAME_PREFIX="dummy_"
DOCKER_IMAGES=$(docker image ls --format "table {{.Repository}}:{{.Tag}}")

if [[ $# -gt 0 ]]
then
  while getopts 'c:context:r:rebuild' option
  do
  	case $option in
  		c|context)
  			if [[ $OPTARG == "test" ]]
  			then
          TEST_CONTEXT="TRUE"
          RUNNING_ENV="test"
          SWARM_NETWORK_NAME="test_dummy-network"
          HOST_NETWORK_NAME="test_host"
  				ERLANG_COOKIE_NAME="test_erlang_cookie"
          NGINX_CERTS_FOLDER="nginx/test_certs"
          DOCKER_COMPOSE_FILE_PATH="./test_docker-compose.yml"
					MONGO_DB="test_dummy_movies"
          shift
  			fi
          echo ""
  			;;
      r|rebuild)
        ;;
  		*) echo "Unknow parameter: $option $OPTARG"
  			usage
  			;;
  	esac
  done
fi


create_self_signed_certs_if_missing() {
  # Argument 1 is the path of NGINX certs folder
  if [[ -z "$(ls -A $1)" ]]
  then
    echo -e "$GREEN[+] [$RUNNING_ENV] Create dummy self signed certs $RESET"
    ./nginx/self_signed_cert_maker.sh $1 &> /dev/null
  else
    echo -e "$YELLOW[+] [$RUNNING_ENV] Dummy self signed certs already created $RESET"
  fi
}


create_docker_images_if_not_built_yet() {
  # Docker swarm needs images to be created before building the stack
  if ! echo "$DOCKER_IMAGES" | grep -E "$1" &>/dev/null
  then
			echo -e "$GREEN[-] [$RUNNING_ENV] Image $1 does not exist, we build it $RESET"
      case "$1" in
        "dummy_mongo:latest")
          docker build -t dummy_mongo:latest -f ./mongodb/Dockerfile . &>/dev/null
          ;;
        "dummy_redis:latest")
          docker build -t dummy_redis:latest -f ./redis/Dockerfile . &>/dev/null
          ;;
        "dummy_nginx:latest")
          docker build -t dummy_nginx:latest -f ./nginx/Dockerfile . &>/dev/null
          ;;
        "dummy_flask:latest")
          docker build -t dummy_flask:latest -f ./gunicorn_flask/flask_celery_client.Dockerfile . &>/dev/null
          ;;
        "dummy_celery_worker:latest")
          docker build -t dummy_celery_worker:latest -f ./celery_client_and_worker/celery_worker.Dockerfile . &>/dev/null
          ;;
        *)
          echo -e "$RED[-] [$RUNNING_ENV] Image $1 is not part of the stack $RESET"
      esac
      DOCKER_IMAGES=$(docker image ls --format "table {{.Repository}}:{{.Tag}}")
  else
      echo -e "$YELLOW[+] [$RUNNING_ENV] Image $1 exists $RESET"
  fi
}


delete_docker_image_for_rebuild() {
  # Executed when user ask for docker images to be rebuild
  DOCKER_IMAGES=$(docker image ls --format "table {{.Repository}}:{{.Tag}}")
  if echo "$DOCKER_IMAGES" | grep -E "$1" &>/dev/null
  then
    echo -e "$GREEN[+] [$RUNNING_ENV] Removing the docker image $1:latest $RESET"
    docker image rm $1:latest &>/dev/null
    sleep 2
  else
    echo -e "$GREEN[+] [$RUNNING_ENV] Docker image $1:latest already removed $RESET"
  fi
}


get_docker_images_name_to_rebuild() {
  # Used by check_if_user_ask_for_rebuild function
  while [[ $# -gt 0 ]]
  do
		delete_docker_image_for_rebuild $DOCKER_IMAGE_NAME_PREFIX$1
		DOCKER_IMAGES=$(docker image ls --format "table {{.Repository}}:{{.Tag}}")
    create_docker_images_if_not_built_yet "$DOCKER_IMAGE_NAME_PREFIX$1:latest"
		DOCKER_IMAGES=$(docker image ls --format "table {{.Repository}}:{{.Tag}}")
    shift
  done
}


check_if_user_ask_for_rebuild() {
  # If user set argument to -r or --rebuild he will ask to rebuild 1 or more Docker images
  # Usage: check_if_user_ask_for_rebuild -r [nginx mongo redis flask celeryçworker]
  while [[ $# -gt 0 ]]
  do
    case "$1" in
      -r|--rebuild)
				shift
        echo -e "$GREEN[+] [$RUNNING_ENV] Rebuild required for docker images: $@"
        get_docker_images_name_to_rebuild "$@"
        ;;
      *)
        shift
        ;;
    esac
  done
}

echo -e "$WHITE[+] [$RUNNING_ENV] Ensure docker swarm is not at used $RESET"
SWARM_STATE=$(docker info --format '{{.Swarm.LocalNodeState}}')
if ! [[ $SWARM_STATE == 'inactive' ]]
then
	docker swarm leave --force &>/dev/null
fi

echo -e "$WHITE[+] [$RUNNING_ENV] Initializing docker swarm $RESET"
docker swarm init --advertise-addr=$SWARM_IP &>/dev/null
echo -e "$GREEN[+] [$RUNNING_ENV] Docker swarm initialized $RESET"

echo -e "$WHITE[+] [$RUNNING_ENV] Creating $SWARM_NETWORK_NAME docker network $RESET"
docker network create -d overlay $SWARM_NETWORK_NAME &>/dev/null
echo -e "$GREEN[+] [$RUNNING_ENV] Docker network '$SWARM_NETWORK_NAME' created $RESET"

if [[ $TEST_CONTEXT == "TRUE" ]]
then
  echo -e "$WHITE[+] [$RUNNING_ENV] Creating $HOST_NETWORK_NAME docker network $RESET"
  docker network create -d overlay $HOST_NETWORK_NAME &>/dev/null
  echo -e "$GREEN[+] [$RUNNING_ENV] Docker network '$HOST_NETWORK_NAME' created $RESET"
fi

echo -e "$WHITE[+] [$RUNNING_ENV] Checking if a rebuild of docker images is required $RESET"
if [[ $# -gt 0 ]]; then USER_USED_ARGS="TRUE"; check_if_user_ask_for_rebuild "$@"; fi
if [[ "$USER_USED_ARGS" = "FALSE" ]];then echo -e "$GREEN[+] No rebuild required $RESET"; fi

echo -e "$WHITE[+] [$RUNNING_ENV] Checking if NGINX cert files exist in: .$NGINX_CERTS_FOLDER/$RESET"
create_self_signed_certs_if_missing $NGINX_CERTS_FOLDER

echo -e "$WHITE[+] [$RUNNING_ENV] Ensuring docker images exist $RESET"
create_docker_images_if_not_built_yet "dummy_mongo:latest"
create_docker_images_if_not_built_yet "dummy_redis:latest"
create_docker_images_if_not_built_yet "dummy_nginx:latest"
create_docker_images_if_not_built_yet "dummy_flask:latest"
create_docker_images_if_not_built_yet "dummy_celery_worker:latest"

echo -e "$WHITE[+] [$RUNNING_ENV] Waiting 3 seconds for the stack to be initialized $RESET"
sleep 3

echo -e "$WHITE[+] [$RUNNING_ENV] Attaching a docker secret for $ERLANG_COOKIE_NAME $RESET"
openssl rand -hex 50 | docker secret create $ERLANG_COOKIE_NAME - &>/dev/null
echo -e "$GREEN[+] [$RUNNING_ENV] Docker secret for $ERLANG_COOKIE_NAME attached $RESET"

echo -e "$WHITE[+] [$RUNNING_ENV] Deploying the swarm stack $RESET"
docker stack deploy --detach -c ./$DOCKER_COMPOSE_FILE_PATH dummy_flask_rabbitmq_celery &> /dev/null
sleep 20
echo -e "$GREEN[+] [$RUNNING_ENV] The swarm stack is deployed $RESET"


echo -e "$WHITE[+] [$RUNNING_ENV] Displaying the swarm stack services states $RESET"
docker service ls
