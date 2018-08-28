from setuptools import setup

setup(name = 'wordpress-cd-k8s',
    version = '0.0.2',
    description = 'Wordpress CD driver to deploy sites via Kubernetes deployments.',
    author = 'Ross Golder',
    author_email = 'ross@golder.org',
    url = 'https://github.com/rossigee/wordpress-cd-k8s',
    install_requires = [
      'wordpress-cd'
    ],
    packages = [
      'wordpress_cd_k8s',
    ]
)
