FROM python:3.11-bullseye

COPY . /hermes

WORKDIR /hermes

RUN pip install .

CMD ["python", "-m", "hermes", "start"]
