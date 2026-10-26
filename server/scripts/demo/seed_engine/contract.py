"""Reads a market folder: contract.yaml (or contract.json on an instance) and the content files."""

import json
import os
import sys


class Market:
    def __init__(self, folder):
        self.dir = os.path.abspath(folder)
        self.contract = load_contract(self.dir)

    def path(self, relative):
        return os.path.join(self.dir, relative)

    def get(self, dotted, default=None):
        node = self.contract
        for key in dotted.split("."):
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    def require(self, dotted):
        value = self.get(dotted)
        if value in (None, "", [], {}):
            sys.exit("the contract needs `%s`" % dotted)
        return value

    def content(self, dotted):
        """The JSON list a `sample_content` entry points at, or [] when the contract names none."""
        relative = self.get(dotted)
        if not relative:
            return []
        with open(self.path(relative), encoding="utf-8") as handle:
            return json.load(handle)

    @property
    def id(self):
        return self.require("market.id")

    @property
    def product(self):
        return self.require("product.name")

    @property
    def slug(self):
        """Folder and file name for product specific files in a branch, such as client/briefdesk."""
        return "".join(ch for ch in self.product.lower() if ch.isalnum())

    @property
    def language(self):
        return self.get("fiction.language") or "en"

    @property
    def timezone(self):
        return self.get("fiction.timezone") or "UTC"


def load_contract(folder):
    yaml_file = os.path.join(folder, "contract.yaml")
    json_file = os.path.join(folder, "contract.json")
    if os.path.exists(yaml_file):
        try:
            import yaml
        except ImportError:
            if not os.path.exists(json_file):
                sys.exit(
                    "PyYAML is missing and there is no contract.json. Use the kit's venv: .venv/bin/python"
                )
        else:
            with open(yaml_file, encoding="utf-8") as handle:
                return yaml.safe_load(handle)
    if os.path.exists(json_file):
        with open(json_file, encoding="utf-8") as handle:
            return json.load(handle)
    sys.exit("no contract.yaml or contract.json in %s" % folder)
