#!/bin/bash

export HOST_PORT=8888
export CONTAINER_PORT=8888
export DEBUG_HOST_PORT=8887

export NOTEBOOK_DIR=./notebooks
export registry=myregistry.io
export versionNumber=beta

export dockerfile_src=$1
export dockerfile_target=$2

export repositoryName=test_ipywidgets

export PERMANENT_STORAGE=./permanent_storage

docker-compose --project-name ${dockerfile_target} build
docker-compose --project-name ${dockerfile_target} up

# read  -n 1 -p "Input Selection:" mainmenuinput

docker-compose --project-name ${dockerfile_target} down
