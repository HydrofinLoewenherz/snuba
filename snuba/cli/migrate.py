import logging
import sys
import click
from clickhouse_driver import Client

from snuba import settings
from snuba.datasets.factory import get_dataset
from snuba.datasets.schema import local_dataset_mode


@click.command()
@click.option('--log-level', default=settings.LOG_LEVEL, help='Logging level to use.')
def migrate(log_level):
    from snuba.migrate import logger, run
    # TODO: this only supports one dataset so far. More work is needed for the others.
    dataset = get_dataset('events')
    logging.basicConfig(level=getattr(logging, log_level.upper()), format='%(asctime)s %(message)s')

    if not local_dataset_mode():
        logger.error("The migration tool can only work on local dataset mode.")
        sys.exit(1)

    host, port = settings.CLICKHOUSE_SERVER.split(':')
    clickhouse = Client(
        host=host,
        port=port,
    )

    table = dataset.get_schema().get_local_table_name()
    run(clickhouse, table)
