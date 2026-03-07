# ChromoRetriever

<p align="center">
  <!-- PyPI version -->
  <a href="https://pypi.org/project/ChromoRetriever">
    <img src="https://img.shields.io/pypi/v/ChromoRetriever.svg?label=PyPI" alt="PyPI" />
  </a>

  <!-- DOI -->
  <a href="https://doi.org/10.5281/zenodo.18897311">
    <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.18897311.svg" alt="DOI" />
  </a>

  <!-- Security -->
  <a href="https://socket.dev/pypi/package/ChromoRetriever">
    <img src="https://badge.socket.dev/pypi/package/ChromoRetriever/artifact_id=tar-gz#1764083045680" alt="Socket" />
  </a>

  <!-- Downloads -->
  <a href="https://pepy.tech/project/ChromoRetriever">
    <img src="https://static.pepy.tech/badge/ChromoRetriever" alt="Downloads" />
  </a>

  <!-- License -->
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  </a>
</p>

ChromoRetriever is a lightweight Python library and CLI for retrieving chromosome-level sequence metadata from the NCBI Datasets API and exporting it to CSV or TSV. It is designed for bioinformatics workflows that need a simple way to pull chromosome tables for one or many genome assemblies.

## Features

- Retrieve chromosome-level sequence reports from NCBI Datasets
- Support single-accession and batch workflows
- Export to CSV or TSV
- Filter out unplaced assembled sequences by default
- Preserve clean chromosome ordering for common naming conventions
- Use as either a Python library or a command-line tool

## Installation

### From a local checkout

```bash
pip install .
```

### Development install

```bash
pip install -e .[dev]
```

## Command-line usage

### Single accession

```bash
chromoretriever GCF_000001735.4
```

This writes `GCF_000001735.4_chromosomes.csv` in the current directory.

### Batch mode

```bash
chromoretriever --file examples/genomes.txt --output chromosomes.csv
```

### Include unplaced assembled sequences

```bash
chromoretriever GCF_000001735.4 --include-unplaced
```

### Export as TSV

```bash
chromoretriever GCF_000001735.4 --format tsv
```

### Exclude columns

```bash
chromoretriever GCF_000001735.4 --exclude-col refseq "gc_content_percent"
```

## Python usage

```python
from chromoretriever import NCBIDatasetsClient, export_records

client = NCBIDatasetsClient()
result = client.fetch_chromosome_table("GCF_000001735.4")

print(result.organism_name)
print(len(result.records))

export_records(result.records, "arabidopsis.csv")
```

### Batch processing from Python

```python
from chromoretriever import process_genome_ids

results = process_genome_ids(
    genome_ids=["GCF_000001735.4", "GCF_009914755.1"],
    output_path="chromosomes.tsv",
    fmt="tsv",
)

for result in results:
    print(result.genome_id, result.organism_name, len(result.records))
```

## Output columns

- `genome_id`
- `taxon`
- `hromosome`
- `genbank`
- `refseq`
- `size_bp`
- `gc_content_percent`

## Project structure

```text
ChromoRetriever/
├── src/chromoretriever/
│   ├── __init__.py
│   ├── api.py
│   ├── cli.py
│   ├── export.py
│   ├── models.py
│   └── utils.py
├── tests/
├── examples/
├── pyproject.toml
└── README.md
```

## API notes

The current implementation uses these NCBI Datasets endpoints:

- `/genome/accession/{accession}/sequence_reports`
- `/genome/accession/{accession}/dataset_report`

If NCBI changes the API contract, the client may need to be adjusted.

## Development

Run tests:

```bash
pytest
```

Build distributions:

```bash
python -m build
```

## License

MIT License. See [LICENSE](LICENSE).
