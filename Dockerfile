FROM node:lts as frontend

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN corepack enable

COPY . /hermes

WORKDIR /hermes

RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile

RUN pnpm build

FROM python:3.12

COPY --from=frontend /hermes /hermes

WORKDIR /hermes

RUN pip install .

EXPOSE 8000

ENTRYPOINT ["uvicorn", "hermes:app", "--host", "0.0.0.0", "--workers", "3"]
