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
            self.image_uri = os.environ['WPCD_DOCKER_IMAGE']
            self.k8s_endpoint_url = os.environ['K8S_ENDPOINT_URL']
        except KeyError as e:
            raise Exception("Missing '{0}' environment variable.".format(e))

        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.image_uri = self.image_uri.replace("{uid}", randomword(6))
        self.image_uri = self.image_uri.replace("{ts}", ts)
        self.mysql_root_pass = randomword(10)

    def _get_docker_compose_yml(self, docker_image):
        with open("config/k8s/docker-compose.yml") as f:
            docker_compose_yml = f.read()
        docker_compose_yml = docker_compose_yml.replace("{{ docker_image }}", docker_image)
        docker_compose_yml = docker_compose_yml.replace("{{ mysql_root_pass }}", self.mysql_root_pass)
        docker_compose_yml = docker_compose_yml.replace("{{ mysql_user }}", self.test_dataset.mysql_user)
        docker_compose_yml = docker_compose_yml.replace("{{ mysql_pass }}", self.test_dataset.mysql_pass)
        docker_compose_yml = docker_compose_yml.replace("{{ mysql_db }}", self.test_dataset.mysql_db)
        return docker_compose_yml

    def _get_k8s_compose_yml(self):
        with open("config/k8s/k8s-compose.yml") as f:
            k8s_compose_yml = f.read()
        k8s_compose_yml = k8s_compose_yml.replace("{{ hostname }}", self.test_site_fqdn)
        return k8s_compose_yml

    def _docker_build(self):
        buildargs = ['docker', 'build', '-t', self.image_uri, '.']
        buildenv = os.environ.copy()
        buildproc = subprocess.Popen(buildargs, stderr=subprocess.PIPE, env=buildenv)
        buildproc.wait()
        exitcode = buildproc.returncode
        errmsg = buildproc.stderr.read()
        if exitcode != 0:
            raise Exception("Error while building image: %s" % errmsg)

    def _docker_push(self):
        pushargs = ['docker', 'push', self.image_uri]
        pushenv = os.environ.copy()
        pushproc = subprocess.Popen(pushargs, stderr=subprocess.PIPE, env=pushenv)
        pushproc.wait()
        exitcode = pushproc.returncode
        errmsg = pushproc.stderr.read()
        if exitcode != 0:
            raise Exception("Error while pushing image: %s" % errmsg)

    def _upgrade_k8s_service(self, namespaceId, deploymentId):
        # Use Kubernetes API call to update a deployment:
        # http://k8s-endpoint/apis/extensions/v1beta1/namespaces/<namespace>/deployments/<deployment>

        endpoint_url = "{0}/apis/apps/v1/namespaces/{1}/deployments/{2}".format(self.k8s_endpoint_url, namespaceId, deploymentId)
        token = os.environ['K8S_TOKEN']
        container_name = os.environ['K8S_CONTAINER']
        headers = {
            'Content-Type': 'application/strategic-merge-patch+json',
            'Authorization': "Bearer " + token
        }
        payload = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": container_name,
                            "image": self.image_uri
                        }]
                    }
                }
            }
        }

        # Upgrade the service with payload
        _logger.info("Updating container '{}' to use image '{}'... ".format(container_name, self.image_uri))
        r = requests.patch(endpoint_url, data=json.dumps(payload), headers=headers)
        res = r.json()
        if r.status_code != 200:
            raise Exception("Unexpected HTTP status code: {}".format(r.status_code))

    def deploy_site(self):
        _logger.info("Deploying site to Kubernetes environment (job id: {0})...".format(self.job_id))

        #_logger.info("Building new docker image...")
        self._docker_build()

        #_logger.info("Pushing new docker image...")
        self._docker_push()

        _logger.info("Deploying new docker image to k8s service...")
        namespaceId = os.environ['K8S_NAMESPACE']
        deploymentId = os.environ['K8S_DEPLOYMENT']
        self._upgrade_k8s_service(namespaceId, deploymentId)

        # Done
        _logger.info("Deployment successful.")
        return 0

    def _setup_ssl(self):
        # Already covered by wildcard cert on LB
        pass

    def _teardown_ssl(self):
        pass
