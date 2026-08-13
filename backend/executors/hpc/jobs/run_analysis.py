#!/usr/bin/env python3
"""
HPC runner script for the drc_timepoint analysis.
Called by submit_drc.sh with a config JSON path as the only argument.

Usage: python3 run_analysis.py /path/to/config.json
"""

import sys
import json
import os

BASE_DIR = "/gpfs/helios/home/hamza/projects/analytics-hub"
sys.path.insert(0, f"{BASE_DIR}/backend")

from external_tools.drc_timepoint import run_analysis_from_config

if len(sys.argv) != 2:
    print("ERROR: Expected exactly one argument — the config JSON path.")
    print("Usage: python3 run_analysis.py <config_path>")
    sys.exit(1)

config_path = sys.argv[1]

if not os.path.exists(config_path):
    print(f"ERROR: Config file not found: {config_path}")
    sys.exit(1)

with open(config_path) as f:
    config = json.load(f)

print(f"Input file : {config['file_path']}")
print(f"Output path: {config['output_path']}")

result_df = run_analysis_from_config(config)

output_path = config["output_path"]
os.makedirs(os.path.dirname(output_path), exist_ok=True)
result_df.to_json(output_path, orient="records", indent=2)

print(f"Done. {len(result_df)} result rows written to: {output_path}")
