from hachoir.stream import InputIOStream
from hachoir.parser import guessParser
from hachoir.metadata import extractMetadata
from flask import json
import logging


logger = logging.getLogger(__name__)


def get_meta(filestream):
    metadata = {}

    try:
        filestream.seek(0)
        stream = InputIOStream(filestream, None, tags=[])
        parser = guessParser(stream)
        if not parser:
            return metadata

        tags = extractMetadata(parser).exportPlaintext(human=False, line_prefix='')
        for text in tags:
            try:
                json.dumps(text)
                key, value = text.split(':', maxsplit=1)
                key, value = key.strip(), value.strip()
                if key and value:
                    metadata.update({key: value})
            except Exception as ex:
                logger.exception(ex)
    except Exception as ex:
        logger.exception(ex)
        return metadata
    return metadata
