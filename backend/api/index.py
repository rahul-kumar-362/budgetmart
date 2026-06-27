"""Vercel serverless entry point.

@vercel/python looks for a module-level WSGI callable named ``app`` in this file
and wraps it as a serverless function. All real logic lives in the app factory.
"""
from api.app_factory import create_app

app = create_app()
