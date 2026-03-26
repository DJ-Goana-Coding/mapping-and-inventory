"""
District 01 — COMMAND_INPUT node package.

Provides the live-ingestion watcher that monitors this district for incoming
Symbolic Instruction Sets (SIS) and ``!: START_HARVEST`` trigger files.
All execution commands are gated by the Zero-Trust Lock before dispatch.
"""
