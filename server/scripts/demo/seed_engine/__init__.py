"""The Superdesk seed engine: one market contract in, a seeded Superdesk instance out.

Standard library only, so the same package runs from a laptop and, copied into a distribution
branch by `build.py superdesk branch`, on the instance itself. PyYAML is used when it is there to
read contract.yaml; on an instance the branch carries contract.json instead.
"""
