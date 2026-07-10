"""Grounded Prompt Columns: a prototype that makes a Dataverse prompt column
grounded, cited, and cheap to keep fresh.

Runs in two modes:
  - mock  : in-memory sample data, no org, no dependencies (great for demos)
  - live  : against a real Dataverse org via the Web API (needs auth + deps)

See README.md for the disclosure and the mapping to the proposed native feature.
"""
__version__ = "0.1.0"
