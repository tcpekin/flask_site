# syntax=docker/dockerfile:1

FROM continuumio/miniconda3 as conda

COPY conda-linux-64.lock .
# RUN conda update -y conda
RUN conda create -p /opt/env --copy --file conda-linux-64.lock
RUN conda clean -afy
RUN conda init bash

# this is the distroless party
FROM gcr.io/distroless/base-debian10
COPY --from=conda /opt/env /opt/env

COPY . .
RUN mkdir logs

CMD [ "/opt/env/bin/gunicorn", "-w", "2", "--bind", "0.0.0.0:5001", "blog:app" ]