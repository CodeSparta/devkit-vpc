#!/bin/bash
clear
sudo podman run -it --rm \
    --name devkit-vpc \
    --entrypoint ./breakdown.yml \
    --workdir /root/deploy/terraform/devkit-vpc \
    --volume $(pwd):/root/deploy/terraform/devkit-vpc:z \
    --volume $(pwd)/aws:/root/.aws:z \
  quay.io/cloudctl/konductor:4.7.9
