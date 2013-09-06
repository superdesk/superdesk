"""Superdesk IO"""

def update_ingest():
    from .newsml import Parser
    from .reuters import ReutersService
    from .reuters_token import ReutersTokenProvider
    ReutersService(Parser(), ReutersTokenProvider()).update()
