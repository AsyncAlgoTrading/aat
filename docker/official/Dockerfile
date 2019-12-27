FROM python:3.7
RUN apt-get update
RUN apt-get -y install apt-transport-https sudo
RUN apt-get -y remove python3

RUN wget https://cmake.org/files/v3.15/cmake-3.15.4-Linux-x86_64.sh -q
RUN mkdir /opt/cmake
RUN printf "y\nn\n" | sh cmake-3.15.4-Linux-x86_64.sh --prefix=/opt/cmake > /dev/null
RUN rm -fr cmake*.sh /opt/cmake/doc
RUN rm -fr /opt/cmake/bin/cmake-gui
RUN rm -fr /opt/cmake/bin/ccmake
RUN rm -fr /opt/cmake/bin/cpack
RUN ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
RUN ln -s /opt/cmake/bin/ctest /usr/local/bin/ctest

RUN python3.7 -m pip install numpy pandas cython codecov nose2 mock flake8 pytest pytest-cov traitlets ipywidgets faker psutil zerorpc

# install node
RUN curl -sL https://deb.nodesource.com/setup_10.x | sudo bash -
RUN apt-get -y install nodejs

RUN npm install --global yarn
RUN yarn --version


