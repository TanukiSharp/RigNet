# Overview

This document is about how to run containerized to save you the troubles of setting up a Python environment.

# Prerequisites

If you are running on Windows in WSL2, make sure to follow the instructions on this page to allow running on GPU in a container: https://docs.microsoft.com/en-us/windows/ai/directml/gpu-cuda-in-wsl

## Get necessary assets

As stated in the original [README](./README.md#quick-start) file, download the training data (checkpoints) and extract the ZIP file at the root of this repository, so you have a `checkpoints` folder at the root.

If you do not have this folder, the container build should fail, which is desired.

## Build the container

Open a shell at the root of the repository and execute the following:

```sh
docker-compose build
```

or

```sh
docker build .
```

`docker-compose` is not required to build the container image.

:warning: If you are building on a machine equipped with the Apple M1 CPU (ARM architecture) you might run into issues while building the container. To fix the problem, add the following parameters to the docker build command to create an image with the correct architecture.

```
docker buildx build --platform linux/amd64 .
```

## Runtime input data

First, open the `quick_start.py` source file and look for the line `model_id, bandwidth, threshold = `, and change it to load the model you want, with the parameters you want.

When running the container (with `docker-compose`), your `quick_start` folder (host) is mounted into the container.
The executable will load the 3D mesh files named after `model_id` from the `quick_start` folder. So you need to have `<model_id>_remesh.obj` and `<model_id>_ori.obj` files in the `quick_start` folder before running.

## Run the container

Open a shell at the root of the repository and execute the following:

```sh
docker-compose run rignet
```
