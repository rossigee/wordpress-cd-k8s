# Kubernetes deployment driver

Packages a site build in a container and updates a Kubernetes deployment to use the new container.

Requires the '[wordpress-cd](https://github.com/rossigee/wordpress-cd)' package.

Requires the following environment variables to be made available:

Env var | Description | Example
--------|-------------|--------
IMAGE_URI | The registry URL to push the container to and to tell K8S to pull it from | registry.gitlab.com/myorganisation/myproject:latest
K8S_ENDPOINT_URL | The base URL of the Kubernetes API service | https://k8s.in.yourdomain.com:6443
K8S_TOKEN | The token to use for the 'Authorization' header |
K8S_NAMESPACE | The namespace in which to find the deployment |
K8S_DEPLOYMENT | The name of the deployment which is to be upgraded |
K8S_CONTAINER | The name of the container to be upgraded |

This driver simply patches the image name for the container via the Kubernetes API, which should trigger a rolling upgrade on the deployment.

NOTE: If the IMAGE_URI is not tagged as 'latest' and doesn't change between deployments, Kubernetes will not upgrade the containers.

TIP: Use a variable related to your CI pipeline as the tag in IMAGE_URI.

