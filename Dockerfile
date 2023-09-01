# syntax=docker/dockerfile:1

FROM condaforge/mambaforge as conda
RUN mamba install -c conda-forge conda-lock
COPY conda-lock.yml .
# RUN conda update -y conda
RUN conda-lock install -p /opt/env --mamba --copy conda-lock.yml
RUN conda clean -afy
RUN conda init bash

# this is the distroless party
FROM gcr.io/distroless/base-debian10
COPY --from=conda /opt/env /opt/env

COPY . .

CMD [ "/opt/env/bin/gunicorn", "-w", "2", "--max_requests", "10", "--timeout", '90', "--bind", "0.0.0.0:5001", "blog:app" ]