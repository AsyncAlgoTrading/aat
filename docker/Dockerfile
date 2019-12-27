FROM python:3.7

RUN apt-get update
RUN apt-get -y install apt-transport-https libtbb-dev cmake

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g yarn

RUN apt-get -y remove python3
RUN python3.7 -m pip install numpy pytest

RUN wget https://github.com/pybind/pybind11/archive/v2.2.4.tar.gz >/dev/null 2>&1  || echo "wget failed"
RUN tar xfz v2.2.4.tar.gz
RUN cd pybind11-2.2.4/ && mkdir build && cd build && cmake .. && make -j 4 && make install
