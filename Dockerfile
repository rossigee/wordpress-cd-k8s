FROM rossigee/wordpress-cd

RUN apk -U add docker

# Install the CI scripts
ADD dist /dist
RUN pip install /dist/wordpress-cd-k8s-0.0.1.tar.gz
