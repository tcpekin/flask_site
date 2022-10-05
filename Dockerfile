# syntax=docker/dockerfile:1

FROM continuumio/miniconda3 as conda

COPY conda-linux-64.lock .
RUN conda update -y conda
RUN conda create -p /opt/env --copy --file conda-linux-64.lock
RUN conda clean -afy
RUN conda init bash

# this is the distroless party
# FROM --platform=linux/amd64 gcr.io/distroless/base-debian10
# COPY --from=conda /opt/env /opt/env

# ENV TINI_VERSION v0.16.1
# ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
# RUN chmod +x /usr/bin/tini

COPY . .
# ENTRYPOINT [ "/usr/bin/tini", "--" ]

# FROM --platform=linux/amd64 nginx:latest
# RUN rm /etc/nginx/conf.d/default.conf
# COPY services/nginx/nginx.conf /etc/nginx/
# COPY --from=0 . .

CMD [ "/opt/env/bin/gunicorn", "-w", "2", "--bind", "0.0.0.0:5001", "blog:app" ]