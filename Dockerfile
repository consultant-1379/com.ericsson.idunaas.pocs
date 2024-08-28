# # # # # # # # # # # # # #
# Stage 'python_base'
# # # # # # # # # # # # # #

FROM armdocker.rnd.ericsson.se/proj-ldc/common_base_os/sles:3.55.0-8 AS python_base

ARG REPO=https://arm.sero.gic.ericsson.se/artifactory/proj-ldc-repo-rpm-local/common_base_os/sles/3.55.0-8
ARG NETCAT_REPO=https://download.opensuse.org/repositories/network:utilities/SLE_15_SP3/network:utilities.repo
RUN zypper ar -C -G -f $REPO LDC-CBO-SLES                               \
 && zypper ar -C -G -f $NETCAT_REPO                                     \
 && zypper ref -f -r LDC-CBO-SLES                                       \
 && zypper ref -f -r network_utilities                                  \
 && zypper install -y python39 python39-pip ca-certificates-mozilla     \
 && zypper install -y curl netcat-openbsd less                          \
 && zypper clean --all                                                  \
# Fix pip and python symbolic link
 && ln -s $(which python3.9) $(dirname $(which python3.9))/python       \
 && ln -s $(which python3.9) $(dirname $(which python3.9))/python3      \
 && ln -s $(which pip3.9)    $(dirname $(which pip3.9))/pip             \
 && ln -s $(which pip3.9)    $(dirname $(which pip3.9))/pip3 \
# Install Helm
 && curl -fsSo helm https://get.helm.sh/helm-v3.7.1-linux-amd64.tar.gz \
 && tar -zxvf helm \
 && mv linux-amd64/helm /usr/local/bin && chmod +x /usr/local/bin/helm

# A locale needs to be installed and set for later use by some python packages like click
ENV LC_ALL=en_US.utf-8
ENV LANG=en_US.utf-8


# # # # # # # # # # # # # #
# Stage 'base_application'
# # # # # # # # # # # # # #

FROM python_base AS base_application

RUN mkdir -p /app/ci
WORKDIR /app
COPY aws_credential_rotation/ .
COPY com.ericsson.idunaas.ci/ /app/ci
RUN pip install -r requirements.txt

RUN find /usr -type d -name  "__pycache__" -exec rm -r {} +


FROM base_application AS released_image
EXPOSE 8008
ENTRYPOINT ["python", "./aws_key_rotation.py"]

