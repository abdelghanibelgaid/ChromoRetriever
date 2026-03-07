import argparse
from pathlib import Path
from typing import Sequence

from .api import NCBIDatasetsClient, process_genome_ids
from .export import export_records
from .utils import DEFAULT_COLUMNS, normalize_excluded_columns


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Retrieve chromosome tables from the NCBI Datasets API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  chromoretriever GCF_000001735.4\n"
            "  chromoretriever --file examples/genomes.txt --output chromosomes.csv\n"
            "  chromoretriever GCF_000001735.4 --exclude-col RefSeq 'GC content (%)'\n"
            "  chromoretriever GCF_000001735.4 --include-unplaced --format tsv\n\n"
            f"Available columns: {', '.join(DEFAULT_COLUMNS)}"
        ),
    )
    parser.add_argument("genome_id", nargs="?", help="NCBI genome assembly accession.")
    parser.add_argument("--file", "-f", dest="input_file", help="Text file with one accession per line.")
    parser.add_argument("--output", "-o", dest="output_file", help="Output file path.")
    parser.add_argument(
        "--format",
        dest="fmt",
        default="csv",
        choices=["csv", "tsv"],
        help="Export format for output files.",
    )
    parser.add_argument(
        "--include-unplaced",
        action="store_true",
        help="Include unplaced assembled sequences.",
    )
    parser.add_argument(
        "--exclude-col",
        nargs="+",
        dest="exclude_columns",
        metavar="COLUMN",
        help="Columns to exclude from export. Multiple values and comma-separated values are both supported.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout in seconds.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.genome_id and not args.input_file:
        parser.error("Either genome_id or --file must be provided.")
    if args.genome_id and args.input_file:
        parser.error("Cannot specify both genome_id and --file.")

    exclude_columns = normalize_excluded_columns(args.exclude_columns)
    client = NCBIDatasetsClient(timeout=args.timeout)

    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as handle:
            genome_ids = [line.strip() for line in handle if line.strip()]

        suffix = ".csv" if args.fmt == "csv" else ".tsv"
        output_path = args.output_file or f"chromosomes{suffix}"
        results = process_genome_ids(
            genome_ids=genome_ids,
            output_path=output_path,
            include_unplaced=args.include_unplaced,
            exclude_columns=exclude_columns,
            fmt=args.fmt,
            client=client,
        )
        total_rows = sum(len(result.records) for result in results)
        print(f"Exported {total_rows} rows from {len(results)} genome assemblies to {output_path}")
        return 0

    genome_id = args.genome_id
    result = client.fetch_chromosome_table(genome_id, include_unplaced=args.include_unplaced)
    suffix = ".csv" if args.fmt == "csv" else ".tsv"
    output_path = args.output_file or f"{genome_id}_chromosomes{suffix}"
    export_records(result.records, output_path, fmt=args.fmt, exclude_columns=exclude_columns)
    print(
        f"Exported {len(result.records)} rows for {result.genome_id} "
        f"({result.organism_name}) to {Path(output_path)}"
    )
    return 0
