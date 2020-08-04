#!/bin/bash -x
sudo podman run -it --rm \
    --name shaman-vpc --pull always \
    --volume $(pwd):/root/deploy/terraform/shaman-vpc:z \
    --volume ${HOME}/.aws:/root/.aws:z \
    --entrypoint ./site.yml \
  docker.io/codesparta/konductor \
    -e cluster_name=${cluster_name} \
    -e aws_region=${cluster_region}
