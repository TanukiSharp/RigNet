FROM nvidia/cuda:11.3.1-runtime-ubuntu18.04

ENV DEBIAN_FRONTEND=noninteractive

# Switch to fastest Japanese mirrors.
RUN sed -i 's#http://archive.ubuntu.com/ubuntu/#https://ftp.udx.icscoe.jp/Linux/ubuntu/#' /etc/apt/sources.list

RUN apt update && \
    apt install -y \
        python3 \
        python3-dev \
        python3-pip \
        libgl1 \
        libglib2.0-0 \
        libxmu6 \
        libspatialindex-dev \
        libglu1-mesa \
        xvfb \
        dumb-init \
        && \
    \
    rm -rf /var/lib/apt/lists/ && \
    \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1 && \
    \
    python -m pip install --upgrade pip

RUN pip install --no-cache-dir \
    -f https://download.pytorch.org/whl/torch_stable.html \
    -f https://pytorch-geometric.com/whl/torch-1.7.1+cu110.html \
    numpy \
    scipy \
    matplotlib \
    tensorboard \
    open3d==0.9.0 \
    opencv-python \
    rtree==0.8 \
    trimesh==3.10.2 \
    torch==1.7.1+cu110 \
    torchvision==0.8.2+cu110 \
    torch-geometric==1.7.2 \
    torch-scatter \
    torch-sparse \
    torch-cluster

WORKDIR /app

COPY ./checkpoints/ ./checkpoints
COPY ./datasets/ ./datasets
COPY ./geometric_proc/ ./geometric_proc
COPY ./models/ ./models
COPY ./utils/ ./utils
COPY gen_dataset.py maya_save_fbx.py mst_generate.py quick_start.py run_skinning.py binvox ./

ENTRYPOINT [ "/usr/bin/dumb-init", "-c", "--" ]

CMD [ "/bin/bash" ]
