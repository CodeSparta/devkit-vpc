#!/bin/bash
clear
mkdir aws 2>/dev/null
#sudo rm -rf terraform.tfstate* .terraform
sudo podman run -it --rm \
    --name devkit-vpc \
    --entrypoint ./site.yml \
    --workdir /root/deploy/terraform/devkit-vpc \
    --volume $(pwd)/aws:/root/.aws:z \
    --volume $(pwd):/root/deploy/terraform/devkit-vpc:z \
  quay.io/cloudctl/konductor:4.7.9 $@
