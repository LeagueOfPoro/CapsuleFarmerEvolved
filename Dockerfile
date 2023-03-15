FROM python:3.10-alpine as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

# Install pipenv and compilation dependencies
RUN apk add --no-cache gcc musl-dev && pip install pipenv

# Install python dependencies in /.venv
COPY Pipfile* /
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --ignore-pipfile

FROM python:3.10-alpine as runtime

# Copy virtual env from base stage
COPY --from=base /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Install application into container
COPY . /app
WORKDIR /app

# Run the application
ENTRYPOINT ["python", "src/main.py"]
CMD ["--config", "/config/config.yaml"]