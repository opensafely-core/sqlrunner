import docker
from docker.errors import NotFound


class Containers:
    def __init__(self):
        self._docker = docker.from_env()

    def get_container(self, name):
        return self._docker.containers.get(name)

    def is_running(self, name):
        try:
            container = self.get_container(name)
            return container.status == "running"  # pragma: no cover
        except NotFound:  # pragma: no cover
            return False

    def get_mapped_port_for_host(self, name, container_port):
        container_port = f"{container_port}/tcp"
        container = self.get_container(name)
        port_config = container.attrs["NetworkSettings"]["Ports"][container_port]
        host_port = port_config[0]["HostPort"]
        return host_port

    def get_container_ip(self, name):
        container = self.get_container(name)
        return container.attrs["NetworkSettings"]["IPAddress"]

    def run_bg(self, name, image, **kwargs):  # pragma: no cover
        return self._run(name=name, image=image, detach=True, **kwargs)

    def _run(self, **kwargs):  # pragma: no cover
        return self._docker.containers.run(remove=True, **kwargs)
