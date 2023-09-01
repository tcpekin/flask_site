# syntax=docker/dockerfile:1

FROM condaforge/mambaforge as conda

COPY conda-linux-64.lock .
# RUN conda update -y conda
RUN conda create -p /opt/env --copy --file conda-linux-64.lock
RUN conda clean -afy
RUN conda init bash

# this is the distroless party
FROM gcr.io/distroless/base-debian10
COPY --from=conda /opt/env /opt/env

COPY . .

CMD [ "/opt/env/bin/gunicorn", "-w", "2", "--max_requests", "10", "--timeout", '90', "--bind", "0.0.0.0:5001", "blog:app" ]