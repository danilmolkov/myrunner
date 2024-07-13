ARG PY_VERSION=3.10
FROM python:${PY_VERSION} as tester

WORKDIR /myrunner

COPY . .

ARG VERSION
RUN --mount=type=bind,source=./dist,target=/myrunner python3 -m pip install /myrunner/myrunner-${VERSION}-py3-none-any.whl --no-cache-dir

CMD [ "python", "-m", "unittest", "discover" ]