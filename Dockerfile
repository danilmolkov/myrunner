FROM python:3.10 as production

COPY ./dist .

ARG VERSION
RUN --mount=type=bind,source=./dist,target=/myrunner python3 -m pip install /myrunner/myrunner-${VERSION}-py3-none-any.whl --no-cache-dir

ENTRYPOINT [ "myrunner" ]
CMD [ "--help" ]