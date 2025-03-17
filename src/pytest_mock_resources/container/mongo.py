from typing import ClassVar, Iterable

from pytest_mock_resources.compat import pymongo
from pytest_mock_resources.config import DockerContainerConfig, fallback
from pytest_mock_resources.container.base import ContainerCheckFailed


class MongoConfig(DockerContainerConfig):
    """Define the configuration object for mongo.

    Args:
        image (str): The docker image:tag specifier to use for mongo containers.
            Defaults to :code:`"mongo:3.6"`.
        host (str): The hostname under which a mounted port will be available.
            Defaults to :code:`"localhost"`.
        port (int): The port to bind the container to.
            Defaults to :code:`28017`.
        ci_port (int): The port to bind the container to when a CI environment is detected.
            Defaults to :code:`27017`.
        root_database (str): The name of the root mongo database to create.
            Defaults to :code:`"dev-mongo"`.
        as_replica_set (bool): Whether to run the mongo container as a replica set.
            Defaults to :code:`False`.
    """

    name = "mongo"

    _fields: ClassVar[Iterable] = {"image", "host", "port", "ci_port", "root_database", "as_mongo_replica_set",
}
    _fields_defaults: ClassVar[dict] = {
        "image": "mongo:3.6",
        "port": 28017,
        "ci_port": 27017,
        "root_database": "dev-mongo",
        "as_mongo_replica_set": False,
    }

    @fallback
    def root_database(self):
        raise NotImplementedError()
    
    @fallback
    def as_mongo_replica_set(self):
        raise NotImplementedError()

    def ports(self):
        return {27017: self.port}

    def check_fn(self):
        try:
            if self.as_mongo_replica_set:
                client = pymongo.MongoClient(self.host, self.port, timeoutMS=1000, directConnection=True)
            else:
                client = pymongo.MongoClient(self.host, self.port, timeoutMS=1000)
            db = client[self.root_database]
            db.command("ismaster")
        except pymongo.errors.PyMongoError:
            raise ContainerCheckFailed(
                f"Unable to connect to a presumed MongoDB test container via given config: {self}"
            )
