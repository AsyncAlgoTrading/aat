FROM timkpaine/aat-deps:latest

WORKDIR /usr/src/app
ADD . /usr/src/app

RUN python3 -m pip install -e .[dev]

RUN make lint
RUN make tests
RUN codecov --token caa422e7-7543-4adb-8ee1-e4a7ea24b988
