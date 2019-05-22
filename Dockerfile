FROM timkpaine/aat:latest

WORKDIR /usr/src/app
ADD . /usr/src/app

RUN python3 -m pip install -U codecov coverage pytest pytest-cov mock flake8 pylint
RUN python3 -m pip install -r requirements.txt

RUN make build
RUN make test
RUN codecov --token caa422e7-7543-4adb-8ee1-e4a7ea24b988
