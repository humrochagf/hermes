FROM oven/bun:1 AS frontend

COPY . /hermes

WORKDIR /hermes

RUN bun install && bun run build

FROM python:3.13

COPY --from=frontend /hermes /hermes

WORKDIR /hermes

RUN pip install .

EXPOSE 8000

ENTRYPOINT ["uvicorn", "hermes:build_app", "--host", "0.0.0.0", "--workers", "3", "--proxy-headers", "--forwarded-allow-ips=*"]
