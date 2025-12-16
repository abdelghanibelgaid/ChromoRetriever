# NCBI Chromosome Exporter

A Python tool for fetching chromosome data from NCBI Datasets API and exporting it to CSV format. Supports batch processing of multiple genome assemblies with customizable output options.

## Features

- Fetch chromosome data from NCBI Datasets API
- Support for both single genome and batch processing
- Automatic pagination handling for large genomes
- Customizable column selection
- Smart chromosome sorting (numeric, linkage groups, sex chromosomes)
- Filter unplaced scaffolds by default
- Machine-friendly CSV output format

## Installation

### Requirements

- Python 3.7 or higher
- `requests` library

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ncbi-chromosome-exporter.git
cd ncbi-chromosome-exporter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Single Genome

Export chromosome data for a single genome assembly:

```bash
python ncbi_chromosome_exporter.py GCA_023547065.1
```

### Batch Processing

Process multiple genomes from a file (one assembly ID per line):

```bash
python ncbi_chromosome_exporter.py --file list.txt --output results.csv
```

### Advanced Options

**Exclude specific columns:**
```bash
python ncbi_chromosome_exporter.py GCA_023547065.1 --exclude-col RefSeq "GC content (%)"
```

**Include unplaced scaffolds:**
```bash
python ncbi_chromosome_exporter.py --file list.txt --include-unplaced
```

**Combine multiple options:**
```bash
python ncbi_chromosome_exporter.py --file list.txt --output chromosomes.csv --include-unplaced --exclude-col RefSeq
```

### Command-Line Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `genome_id` | - | NCBI genome assembly ID (e.g., GCA_023547065.1) |
| `--file` | `-f` | File containing genome IDs (one per line) |
| `--output` | `-o` | Output CSV file path |
| `--include-unplaced` | - | Include unplaced scaffolds (default: only chromosomes) |
| `--exclude-col` | - | Space or comma-separated list of columns to exclude |

### Available Columns

- `GenomeID` - NCBI assembly accession
- `Taxon` - Organism scientific name
- `Chromosome` - Chromosome name/number
- `GenBank` - GenBank accession
- `RefSeq` - RefSeq accession
- `Size (bp)` - Chromosome length in base pairs
- `GC content (%)` - GC percentage

## Input Format

For batch processing, create a text file with one genome assembly ID per line:

```
GCA_009663005.1
GCA_019202715.1
GCF_000442705.2
GCF_009389715.1
```

## Output Format

The tool generates a CSV file with the following structure:

```csv
GenomeID,Taxon,Chromosome,GenBank,RefSeq,Size (bp),GC content (%)
GCF_000001735.4,Arabidopsis thaliana,1,CP002684.1,NC_003070.9,30427671,36.0
GCF_000001735.4,Arabidopsis thaliana,2,CP002685.1,NC_003071.7,19698289,36.0
```

## Chromosome Sorting

Chromosomes are sorted intelligently:
1. Numeric chromosomes (1, 2, 3, ..., 10, 11, ...)
2. Linkage groups (LG1, LG2, ..., LG10, LG11, ...)
3. Sex chromosomes (X, Y)
4. Mitochondrial (MT, M)
5. Other chromosomes (alphabetically)

## Examples

### Example 1: Single Genome Export
```bash
python ncbi_chromosome_exporter.py GCA_023547065.1
```

Output: `GCA_023547065.1_chromosomes.csv`

### Example 2: Batch Processing
```bash
python ncbi_chromosome_exporter.py --file genomes.txt --output all_chromosomes.csv
```

### Example 3: Custom Column Selection
```bash
python ncbi_chromosome_exporter.py --file genomes.txt --exclude-col "GC content (%)" RefSeq
```

## API Information

This tool uses the NCBI Datasets API v2alpha:
- Sequence Reports endpoint: `/genome/accession/{id}/sequence_reports`
- Dataset Report endpoint: `/genome/accession/{id}/dataset_report`

The API is public and does not require authentication. Rate limits apply as per NCBI usage guidelines.

## Troubleshooting

**No chromosome data found:**
- Verify the assembly ID is correct
- Check if the genome has chromosome-level assembly
- Use `--include-unplaced` to see all sequences

**API timeout errors:**
- The tool automatically retries with pagination
- Large genomes may take longer to process

**Missing columns in output:**
- Some genomes may lack RefSeq accessions or GC content data
- These fields will show as `n/a` or `N/A`

## Contributing

Contributions are welcome. Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

**Author:** Mahmoud Zakaria 🇲🇦  
**Website:** [www.mahmoud.ma](https://www.mahmoud.ma)

## Acknowledgments

- Data provided by NCBI Datasets API
- Built with Python and the requests library
