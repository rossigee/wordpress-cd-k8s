# Kubernetes-based deployment functions

import os
import requests
import json
import base64
import datetime
import subprocess
import logging
_logger = logging.getLogger(__name__)

from wordpress_cd.drivers import driver
from wordpress_cd.drivers.base import BaseDriver, randomword


@driver('k8s')
class KubernetesDriver(BaseDriver):
    def __str__(self):
        return "Kubernetes"

    def __init__(self, args, test_dataset = None):
        super(KubernetesDriver, self).__init__(args, test_dataset = test_dataset)

        _logger.debug("Initialising Kubernetes Deployment Driver")

        try:
            self.k8s_endpoint_url = os.environ['K8S_ENDPOINT_URL']
            self.k8s_token = os.environ['K8S_TOKEN']
        except KeyError as e:
            raise Exception("Missing '{0}' environment variable.".format(e))

        self.mysql_root_pass = randomword(10)

    def _upgrade_k8s_service(self, namespaceId, deploymentId, containerId, imageUri):
        # Use Kubernetes API call to update a deployment:
        # http://k8s-endpoint/apis/extensions/v1beta1/namespaces/<namespace>/deployments/<deployment>

        endpoint_url = "{0}/apis/apps/v1/namespaces/{1}/deployments/{2}".format(self.k8s_endpoint_url, namespaceId, deploymentId)
        headers = {
            'Content-Type': 'application/strategic-merge-patch+json',
            'Authorization': "Bearer " + self.k8s_token
        }
        payload = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": containerId,
                            "image": imageUri
                        }]
                    }
                }
            }
        }

        # Upgrade the service with payload
        _logger.info("Updating container '{}' to use image '{}'... ".format(containerId, imageUri))
        r = requests.patch(endpoint_url, data=json.dumps(payload), headers=headers)
        res = r.json()
        if r.status_code != 200:
            raise Exception("Unexpected HTTP status code: {}".format(r.status_code))

    def deploy_site(self):
        _logger.info("Deploying site to Kubernetes environment (job id: {0})...".format(self.job_id))
        namespace = os.environ['K8S_NAMESPACE']
        deployment = os.environ['K8S_DEPLOYMENT']
        container = os.environ['K8S_CONTAINER']
        image_uri = os.environ['IMAGE_URI']
        self._upgrade_k8s_service(namespace, deployment, container, image_uri)

        # Done
        _logger.info("Deployment successful.")
        return 0

    def _setup_ssl(self):
        # Already covered by wildcard cert on LB
        pass

    def _teardown_ssl(self):
        pass
