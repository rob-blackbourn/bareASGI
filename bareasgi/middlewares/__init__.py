"""Middlewares"""

from .compression import (
    CompressionMiddleware,
    make_default_compression_middleware
)

__all__ = [
    'CompressionMiddleware',
    'make_default_compression_middleware'
]
