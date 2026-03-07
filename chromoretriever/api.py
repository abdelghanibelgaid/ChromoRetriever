from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence

import requests

from .export import export_records
from .models import ChromosomeRecord, FetchResult
from .utils import chromosome_sort_key, normalize_excluded_columns


class NCBIDatasetsClient:
    """Client for retrieving chromosome-level sequence reports from NCBI Datasets."""

    def __init__(
        self,
        base_url: str = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha",
        timeout: int = 30,
        user_agent: str = "ChromoRetriever/0.1.0",
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": user_agent,
            }
        )

    def _get_json(self, endpoint: str, params: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        response = self.session.get(f"{self.base_url}{endpoint}", params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected API response payload")
        return data

    def fetch_all_sequence_reports(self, genome_id: str) -> List[Dict[str, object]]:
        endpoint = f"/genome/accession/{genome_id}/sequence_reports"
        reports: List[Dict[str, object]] = []
        page_token: Optional[str] = None

        while True:
            params = {"page_token": page_token} if page_token else None
            payload = self._get_json(endpoint, params=params)
            current_reports = payload.get("reports", [])
            if not isinstance(current_reports, list):
                raise ValueError("Unexpected reports payload")
            reports.extend(current_reports)

            page_token = payload.get("next_page_token")
            if not page_token:
                break

        return reports

    def fetch_organism_name(self, genome_id: str) -> str:
        endpoint = f"/genome/accession/{genome_id}/dataset_report"
        payload = self._get_json(endpoint)
        reports = payload.get("reports", [])
        if not reports:
            return "Unknown"

        first_report = reports[0]
        if not isinstance(first_report, dict):
            return "Unknown"

        organism = first_report.get("organism", {})
        if not isinstance(organism, dict):
            return "Unknown"

        return str(organism.get("organism_name", "Unknown"))

    def fetch_chromosome_table(
        self,
        genome_id: str,
        include_unplaced: bool = False,
    ) -> FetchResult:
        reports = self.fetch_all_sequence_reports(genome_id)
        organism_name = self.fetch_organism_name(genome_id)

        records: List[ChromosomeRecord] = []
        for sequence in reports:
            if not isinstance(sequence, dict):
                continue

            assigned_location = sequence.get("assigned_molecule_location_type", "")
            role = sequence.get("role", "")
            is_chromosome = assigned_location == "Chromosome"
            is_assembled = role == "assembled-molecule"

            if not is_chromosome and not (include_unplaced and is_assembled):
                continue

            chromosome_name = str(sequence.get("chr_name") or sequence.get("assigned_molecule") or "N/A")
            if not include_unplaced and chromosome_name == "Un":
                continue

            gc_content = sequence.get("gc_percent")
            gc_value = round(float(gc_content), 1) if gc_content is not None else None

            record = ChromosomeRecord(
                genome_id=genome_id,
                taxon=organism_name,
                chromosome=chromosome_name,
                genbank=str(sequence.get("genbank_accession", "N/A")),
                refseq=str(sequence.get("refseq_accession", "N/A")),
                size_bp=int(sequence.get("length", 0) or 0),
                gc_content_percent=gc_value,
            )
            records.append(record)

        records.sort(key=lambda item: chromosome_sort_key(item.chromosome))
        return FetchResult(genome_id=genome_id, organism_name=organism_name, records=records)


def process_genome_ids(
    genome_ids: Sequence[str],
    output_path: str | None = None,
    include_unplaced: bool = False,
    exclude_columns: Sequence[str] | None = None,
    fmt: str = "csv",
    client: Optional[NCBIDatasetsClient] = None,
) -> List[FetchResult]:
    active_client = client or NCBIDatasetsClient()
    normalized_exclusions = normalize_excluded_columns(exclude_columns)

    results: List[FetchResult] = []
    for genome_id in genome_ids:
        accession = genome_id.strip()
        if not accession:
            continue

        result = active_client.fetch_chromosome_table(
            accession,
            include_unplaced=include_unplaced,
        )
        results.append(result)

    if output_path:
        append = False
        for result in results:
            export_records(
                result.records,
                output_path=output_path,
                fmt=fmt,
                append=append,
                exclude_columns=normalized_exclusions,
            )
            append = True

    return results