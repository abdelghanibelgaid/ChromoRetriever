"""Public package interface for ChromoRetriever."""

from .api import NCBIDatasetsClient, process_genome_ids
from .export import export_records
from .models import ChromosomeRecord, FetchResult

__all__ = [
    "ChromosomeRecord",
    "FetchResult",
    "NCBIDatasetsClient",
    "export_records",
    "process_genome_ids",
]

__version__ = "0.1.0"
