import re
from typing import Iterable, List, Mapping, MutableMapping, Sequence

DEFAULT_COLUMNS = [
    "GenomeID",
    "Taxon",
    "Chromosome",
    "GenBank",
    "RefSeq",
    "Size (bp)",
    "GC content (%)",
]

_SPECIAL_CHROMOSOMES = {
    "X": 1000,
    "Y": 1001,
    "MT": 1002,
    "M": 1002,
    "MITO": 1002,
    "MITOCHONDRION": 1002,
}


def normalize_excluded_columns(excluded: Sequence[str] | None) -> List[str]:
    if not excluded:
        return []

    normalized: List[str] = []
    for value in excluded:
        normalized.extend(item.strip() for item in value.split(",") if item.strip())
    return normalized


def chromosome_sort_key(chromosome_name: str):
    name = chromosome_name.replace("chr", "").replace("Chr", "").upper()

    if name in _SPECIAL_CHROMOSOMES:
        return (0, _SPECIAL_CHROMOSOMES[name], "")

    try:
        return (0, int(name), "")
    except ValueError:
        pass

    match = re.match(r"^([A-Z]+)(\d+)$", name)
    if match:
        prefix, number = match.groups()
        return (1, prefix, int(number))

    return (2, name, 0)


def sort_record_dicts(records: Iterable[MutableMapping[str, object]]) -> List[MutableMapping[str, object]]:
    return sorted(records, key=lambda item: chromosome_sort_key(str(item["Chromosome"])))


def filter_columns(record: Mapping[str, object], excluded_columns: Sequence[str] | None) -> MutableMapping[str, object]:
    excluded_set = set(excluded_columns or [])
    return {key: value for key, value in record.items() if key not in excluded_set}