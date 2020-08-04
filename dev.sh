#!/bin/bash -x
clear
#   --entrypoint bash \
sudo podman run -it --rm \
    --name shaman-vpc \
    --entrypoint bash \
    --workdir /root/deploy/terraform/shaman-vpc \
    --volume $(pwd):/root/deploy/terraform/shaman-vpc:z \
  docker.io/codesparta/konductor
