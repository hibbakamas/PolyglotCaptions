# app/utils/metrics.py

import logging

logger = logging.getLogger("polyglot")

def metric_caption_processed():
    logger.info("metric_caption_processed", extra={
        "custom_dimensions": {"count": 1}
    })

def metric_processing_time(ms: int):
    logger.info("metric_processing_time_ms", extra={
        "custom_dimensions": {"ms": ms}
    })
