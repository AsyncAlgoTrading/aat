FROM quay.io/pypa/manylinux2014_x86_64
RUN yum -y install sudo wget

RUN wget https://cmake.org/files/v3.15/cmake-3.15.4-Linux-x86_64.sh -q
RUN mkdir /opt/cmake
RUN printf "y\nn\n" | sh cmake-3.15.4-Linux-x86_64.sh --prefix=/opt/cmake > /dev/null
RUN rm -fr cmake*.sh /opt/cmake/doc
RUN rm -fr /opt/cmake/bin/cmake-gui
RUN rm -fr /opt/cmake/bin/ccmake
RUN rm -fr /opt/cmake/bin/cpack
RUN ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
RUN ln -s /opt/cmake/bin/ctest /usr/local/bin/ctest

RUN rm -rf /opt/python/cp37-cp37m/bin/auditwheel
RUN cp -arf /opt/python/cp37-cp37m/* /usr/local/
ENV PATH=/usr/local/bin:$PATH
RUN python3 -m pip install pybind11 cython codecov mock flake8 pytest pytest-cov traitlets ipywidgets faker psutil zerorpc

# install node
RUN curl -sL https://rpm.nodesource.com/setup_10.x | sudo bash -
RUN yum install -y nodejs

RUN npm install --global yarn
RUN yarn --version
