#!/bin/bash

SERVICE_NAME="iam"
IMAGE_NAME="iam-service"

docker build -t $IMAGE_NAME .
docker rm -f $SERVICE_NAME 2>/dev/null
docker run -d --name $SERVICE_NAME -p 5000:5000 $IMAGE_NAME
