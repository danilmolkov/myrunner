FROM python:3.10 as production

COPY ./dist .

RUN --mount=type=bind,source=./dist,target=/myrunner python3 -m pip install /myrunner/myrunner-${VERSION}-py3-none-any.whl --no-cache-dir

ARG VERSION
LABEL description="Perform runs" \
    author="molkovdanil@gmail.com" \
    myrunner_version=${VERSION}

ENTRYPOINT [ "myrunner" ]
CMD [ "--help" ]