"""Superdesk IO"""

from superdesk import manager

def update_ingest():
    """Update ingest"""
    from .newsml import Parser
    from .reuters import ReutersService
    from .reuters_token import tokenProvider
    ReutersService(Parser(), tokenProvider).update()
