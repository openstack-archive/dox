import docker
import docker.unixconn
from docker.unixconn import unixconn
import requests


def _get_docker_api_version():
    session = requests.Session()
    session.mount(
        "http+unix://",
        docker.unixconn.unixconn.UnixAdapter(
            "http+unix://var/run/docker.sock", 60))
    response = session.get('/version')
    try:
        api_version = response.json()['ApiVersion']
    except KeyError:
        # For now, fall back to 1.10 as a safety net
        api_version = '1.10'
    return api_version


def _version_string_to_tuple(version):
    return tuple([int(f) for f in version.split('.')])

  
class Dox(object):


    def __init__(self):
        self.client = docker.Client(version=_get_docker_api_version())
