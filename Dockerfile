ARG venv_python
FROM python:${venv_python}

LABEL Maintainer="CanDIG Team"
LABEL "candigv2"="chord_metadata_service"

USER root

RUN groupadd -r candig && useradd -r -g candig candig

RUN apt-get update && apt-get -y install \
	postgresql-client
	
RUN mkdir /app
WORKDIR /app

COPY ./requirements /app/requirements

# Conditionally install dependencies based on the environment
ARG katsu_env
RUN if [ ${katsu_env} = "dev" ]; then \
    echo "Installing dev.txt" && \
    pip install --no-cache-dir -r requirements/dev.txt; \
else \
    echo "Installing prod.txt" && \
    pip install --no-cache-dir -r requirements/prod.txt; \
fi


COPY . /app/chord_metadata_service

WORKDIR /app/chord_metadata_service

# Create log and staticfiles directory and adjust permissions
RUN mkdir -p /app/chord_metadata_service/logs /app/chord_metadata_service/staticfiles \
    && chown -R candig:candig /app/chord_metadata_service

RUN chmod +x /app/chord_metadata_service/entrypoint.sh

USER candig

CMD ["/app/chord_metadata_service/entrypoint.sh"]

