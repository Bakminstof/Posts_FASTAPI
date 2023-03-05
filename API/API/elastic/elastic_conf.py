from elastic_transport import NodeConfig

from data import settings

node_config = NodeConfig(
    scheme=settings.ELASTIC_SCHEMA,
    host=settings.ELASTIC_HOST,
    port=settings.ELASTIC_PORT
)

