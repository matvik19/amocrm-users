from loguru import logger
from elasticsearch import Elasticsearch

ELASTICSEARCH_HOST = "http://95.163.231.10:9200"
es_client = Elasticsearch([ELASTICSEARCH_HOST])


def elasticsearch_handler(message):
    """
    Обработчик для отправки логов в Elasticsearch.
    """
    log_record = message.record
    log_data = {
        "@timestamp": log_record["time"].isoformat(),
        "log.level": log_record["level"].name,
        "message": log_record["message"],
        "module": log_record["module"],
        "function": log_record["function"],
        "line": log_record["line"],
    }
    try:
        es_client.index(index="tokens-users-logs", document=log_data)
    except Exception as e:
        logger.error(f"Error sending log to Elasticsearch: {e}")


def setup_logging():
    logger.add(elasticsearch_handler, level="INFO")
    logger.info("Logging setup complete.")
