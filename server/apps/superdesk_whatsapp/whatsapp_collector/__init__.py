import traceback
import logging

from .stack import YowsupCollectStack


logger = logging.getLogger(__name__)


def collect_messages(phone, password):
    results = []
    try:
        stack = YowsupCollectStack(credentials=(phone, password), results=results)
        stack.start()
    except Exception as e:
        logger.critical(e)
        traceback.print_exc()
    return results
