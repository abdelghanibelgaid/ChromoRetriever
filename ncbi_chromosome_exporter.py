#!/usr/bin/env python3
"""
NCBI Genome Chromosome Table Exporter
Fetches chromosome data from NCBI Datasets API and exports to CSV

Author: Mahmoud Zakaria
Website: https://www.mahmoud.ma
"""

import requests
import csv
import sys
import argparse
from typing import List, Dict


def fetch_all_sequence_reports(api_url: str, headers: dict) -> List[Dict]:
    reports = []
    page_token = None
    
    while True:
        params = {}
        if page_token:
            params["page_token"] = page_token
        
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")
            break
        
        reports.extend(data.get("reports", []))
        
        page_token = data.get("next_page_token")
        if not page_token:
            break
    
    return reports


def fetch_chromosome_table(genome_id: str, include_unplaced: bool = False, exclude_columns: List[str] = None) -> tuple:
    api_url = f"https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/{genome_id}/sequence_reports"
    
    print(f"Fetching chromosome data from NCBI Datasets API for: {genome_id}")
    
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (compatible; NCBIChromosomeExporter/1.0)'
        }
        
        reports = fetch_all_sequence_reports(api_url, headers)
        
        if not reports:
            print("No sequence reports found in API response")
            return [], "Unknown"
            
    except Exception as e:
        print(f"Error fetching sequence data: {e}")
        return [], "Unknown"
    
    organism_name = "Unknown"
    try:
        dataset_url = f"https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession/{genome_id}/dataset_report"
        dataset_response = requests.get(dataset_url, headers=headers, timeout=30)
        dataset_response.raise_for_status()
        dataset_data = dataset_response.json()
        
        if dataset_data.get('reports'):
            organism_info = dataset_data['reports'][0].get('organism', {})
            organism_name = organism_info.get('organism_name', 'Unknown')
    except Exception as e:
        print(f"Could not fetch organism name: {e}")
    
    table_data = []
    
    try:
        for seq in reports:
            assigned_molecule_location_type = seq.get('assigned_molecule_location_type', '')
            role = seq.get('role', '')
            
            is_chromosome = assigned_molecule_location_type == "Chromosome"
            is_assembled = role == "assembled-molecule"
            
            if not is_chromosome and not (include_unplaced and is_assembled):
                continue
                    
            chr_name = seq.get('chr_name', seq.get('assigned_molecule', 'N/A'))
            
            if not include_unplaced and chr_name == "Un":
                continue
            
            chrom_data = {
                'GenomeID': genome_id,
                'Taxon': organism_name,
                'Chromosome': chr_name,
                'GenBank': seq.get('genbank_accession', 'N/A'),
                'RefSeq': seq.get('refseq_accession', 'n/a'),
                'Size (bp)': seq.get('length', 0),
                'GC content (%)': round(seq.get('gc_percent', 0), 1) if seq.get('gc_percent') else None
            }
            
            if exclude_columns:
                chrom_data = {k: v for k, v in chrom_data.items() if k not in exclude_columns}
            
            table_data.append(chrom_data)
        
        def sort_key(item):
            import re
            chr_name = item['Chromosome'].replace("chr", "").replace("Chr", "").upper()
            special = {"X": 1000, "Y": 1001, "MT": 1002, "M": 1002, "MITO": 1002, "MITOCHONDRION": 1002}
            
            if chr_name in special:
                return (0, special[chr_name], "")
            
            try:
                return (0, int(chr_name), "")
            except ValueError:
                pass
            
            match = re.match(r'^([A-Z]+)(\d+)$', chr_name)
            if match:
                prefix, num = match.groups()
                return (1, prefix, int(num))
            
            return (2, chr_name, 0)
        
        table_data.sort(key=sort_key)
        
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error parsing chromosome data: {e}")
        import traceback
        traceback.print_exc()
        return [], organism_name
    
    return table_data, organism_name


def export_to_csv(genome_id: str, organism_name: str, table_data: List[Dict[str, str]], output_file: str):
    if not table_data:
        print(f"No chromosome data found for {genome_id}")
        return
    
    headers = list(table_data[0].keys())
    
    file_exists = False
    try:
        with open(output_file, 'r') as f:
            file_exists = True
    except FileNotFoundError:
        pass
    
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        
        if not file_exists or csvfile.tell() == 0:
            writer.writeheader()
        
        writer.writerows(table_data)
        
    print(f"Data exported for {genome_id} ({organism_name}) - {len(table_data)} rows")


def process_genome_list(input_file: str, output_file: str, include_unplaced: bool = False, exclude_columns: List[str] = None):
    with open(output_file, 'w', encoding='utf-8') as f:
        pass
    
    with open(input_file, 'r') as f:
        genome_ids = [line.strip() for line in f if line.strip()]
    
    for genome_id in genome_ids:
        print(f"\nProcessing {genome_id}...")
        table_data, organism_name = fetch_chromosome_table(genome_id, include_unplaced, exclude_columns)
        export_to_csv(genome_id, organism_name, table_data, output_file)
    
    print(f"\n✓ All data exported to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='NCBI Genome Chromosome Table Exporter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single genome, all columns
  python ncbi_chromosome_exporter.py GCA_023547065.1
  
  # Single genome, exclude columns
  python ncbi_chromosome_exporter.py GCA_023547065.1 --exclude-col RefSeq "GC content (%%)"
  
  # Batch processing from file
  python ncbi_chromosome_exporter.py --file list.txt --output chromosomes.csv
  
  # Include unplaced scaffolds
  python ncbi_chromosome_exporter.py --file list.txt --output chromosomes.csv --include-unplaced
  
  # Combine all options
  python ncbi_chromosome_exporter.py --file list.txt --output out.csv --include-unplaced --exclude-col RefSeq

Available columns: GenomeID, Taxon, Chromosome, GenBank, RefSeq, Size (bp), GC content (%%)
        """
    )
    
    parser.add_argument(
        'genome_id',
        nargs='?',
        help='NCBI genome assembly ID (e.g., GCA_023547065.1)'
    )
    parser.add_argument(
        '--file',
        '-f',
        dest='input_file',
        help='File containing genome IDs (one per line)'
    )
    parser.add_argument(
        '--output',
        '-o',
        dest='output_file',
        help='Output CSV file path (default: chromosomes.csv or <genome_id>_chromosomes.csv)'
    )
    parser.add_argument(
        '--include-unplaced',
        action='store_true',
        help='Include unplaced scaffolds (default: only chromosomes)'
    )
    parser.add_argument(
        '--exclude-col',
        nargs='+',
        dest='exclude_columns',
        metavar='COLUMN',
        help='Columns to exclude from output (space or comma-separated)'
    )
    
    args = parser.parse_args()
    
    exclude_columns = None
    if args.exclude_columns:
        exclude_columns = []
        for col in args.exclude_columns:
            exclude_columns.extend([c.strip() for c in col.split(',')])
    
    if not args.genome_id and not args.input_file:
        parser.error('Either genome_id or --file must be provided')
    
    if args.genome_id and args.input_file:
        parser.error('Cannot specify both genome_id and --file')
    
    if args.input_file:
        output_file = args.output_file or 'chromosomes.csv'
        process_genome_list(args.input_file, output_file, args.include_unplaced, exclude_columns)
    else:
        genome_id = args.genome_id
        output_file = args.output_file or f"{genome_id}_chromosomes.csv"
        
        print(f"Processing {genome_id}...")
        table_data, organism_name = fetch_chromosome_table(genome_id, args.include_unplaced, exclude_columns)
        
        if table_data:
            with open(output_file, 'w', encoding='utf-8') as f:
                pass
            
            export_to_csv(genome_id, organism_name, table_data, output_file)
            print(f"✓ Data exported to {output_file} ({organism_name}) - {len(table_data)} rows")
        else:
            print("No chromosome data found")


if __name__ == "__main__":
    main()
