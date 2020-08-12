#!/bin/bash -x
clear
mkdir aws 2>/dev/null
sudo podman run -it --rm \
    --pull always \
    --name devkit-vpc \
    --entrypoint bash \
    --workdir /root/deploy/terraform/devkit-vpc \
    --volume $(pwd):/root/deploy/terraform/devkit-vpc:z \
    --volume $(pwd)/aws/:/root/.aws/:z \
  docker.io/codesparta/konductor
