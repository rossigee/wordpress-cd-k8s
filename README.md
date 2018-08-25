# Kubernetes deployment driver

Packages a site build in a container and updates a Kubernetes deployment to use the new container.

Requires the '[wordpress-cd](https://github.com/rossigee/wordpress-cd)' package.

Requires the following environment variables to be made available:

Env var | Description | Example
--------|-------------|--------
WPCD_DOCKER_IMAGE | The registry URL to push the container to and to tell K8S to pull it from | registry.gitlab.com/myorganisation/myproject:latest
K8S_ENDPOINT_URL | The base URL of the Kubernetes API service | https://k8s.in.yourdomain.com:6443
K8S_TOKEN | The token to use for the 'Authorization' header |
K8S_NAMESPACE | The namespace in which to find the deployment |
K8S_DEPLOYMENT | The name of the deployment which is to be upgraded |
K8S_CONTAINER | The name of the container to be upgraded |

It first invokes 'docker build' to build the image, and 'docker push' to push it to the registry.

Then, it then patches the image name for the container via the Kubernetes API, which should trigger a rolling upgrade on the deployment.

In order for a deployment to update, the image name must change between deployments. Therefore, you can use a dynamic tag in the 'WPCD_DOCKER_IMAGE' variable:

```
export WPCD_DOCKER_IMAGE=registry.yourdomain.com/path/yourapplication:{TS}
```

The above replaces the image tag with a timestamp in the format 'YYYYMMDDHHMMSS'. In addition to `{TS}`, there is `{UID}` which will insert a random 6-char string.
