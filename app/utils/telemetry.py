import logging

from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer


def setup_telemetry(connection_string: str | None):
    logger = logging.getLogger("polyglot")
    logger.setLevel(logging.INFO)

    if connection_string:
        # Logs
        handler = AzureLogHandler(connection_string=f"InstrumentationKey={connection_string}")
        logger.addHandler(handler)

        # Tracing
        Tracer(
            exporter=AzureExporter(connection_string=f"InstrumentationKey={connection_string}"),
            sampler=ProbabilitySampler(1.0),
        )

    return logger
