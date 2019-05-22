FROM timkpaine/aat:latest

WORKDIR /usr/src/app
ADD . /usr/src/app

RUN python3 -m pip install codecov nose2 mock flake8 pylint
RUN python3 -m pip install -r requirements.txt

RUN DOCKER=true make test
RUN codecov --token caa422e7-7543-4adb-8ee1-e4a7ea24b988
