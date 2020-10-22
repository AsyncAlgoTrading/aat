FROM quay.io/pypa/manylinux2010_x86_64
RUN yum -y install sudo wget

RUN rm -rf /opt/python/cp37-cp37m/bin/auditwheel
RUN cp -arf /opt/python/cp37-cp37m/* /usr/local/
ENV PATH=/usr/local/bin:$PATH
RUN python3 -m pip install pybind11 codecov mock flake8 pytest pytest-cov

# install node
RUN curl -sL https://rpm.nodesource.com/setup_10.x | sudo bash -
RUN yum install -y nodejs

RUN npm install --global yarn
RUN yarn --version
