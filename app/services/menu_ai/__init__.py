"""Grounded "Ask AI" menu assistant pipeline.

Modules:
- context_builder: collects + caches real restaurant/menu data for prompting.
- retrieval: lexical retrieval of relevant menu items (no embeddings required).
- assistant: orchestrates retrieval -> prompt -> LLM -> validation -> fallback.
"""
