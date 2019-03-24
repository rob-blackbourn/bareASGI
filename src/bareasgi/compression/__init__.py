from .streaming import (
    make_gzip_compressobj,
    make_deflate_compressobj,
    make_compress_compressobj,
    compression_writer_adapter,
    compression_writer
)

__all__ = [
    'make_gzip_compressobj',
    'make_deflate_compressobj',
    'make_compress_compressobj',
    'compression_writer_adapter',
    'compression_writer'
]