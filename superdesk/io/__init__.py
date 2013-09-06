"""Superdesk IO"""

from .newsml import Parser
from .reuters import ReutersService
from .reuters_token import ReutersTokenProvider

def update_ingest():
    ReutersService(Parser(), ReutersTokenProvider()).update()
