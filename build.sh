#!/bin/bash -x
clear
sudo rm -rf terraform.tfstate* .terraform
sudo podman run -it --rm \
    --name shaman-vpc \
    --entrypoint ./site.yml \
    --workdir /root/deploy/terraform/shaman-vpc \
    --volume $(pwd):/root/deploy/terraform/shaman-vpc:z \
  docker.io/codesparta/konductor
