from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ChromosomeRecord:
    genome_id: str
    taxon: str
    chromosome: str
    genbank: str
    refseq: str
    size_bp: int
    gc_content_percent: Optional[float]

    def to_dict(self) -> Dict[str, object]:
        return {
            "genome_id": self.genome_id,
            "taxon": self.taxon,
            "chromosome": self.chromosome,
            "genbank": self.genbank,
            "refseq": self.refseq,
            "size_bp": self.size_bp,
            "gc_content_percent": self.gc_content_percent,
        }


@dataclass(frozen=True)
class FetchResult:
    genome_id: str
    organism_name: str
    records: List[ChromosomeRecord]