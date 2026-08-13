#!/bin/bash
#SBATCH --partition=testing
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --job-name=analytics_hub_timepoint

# Config JSON path is passed as first argument ($1)
CONFIG=${1:-""}

if [ -z "$CONFIG" ]; then
    echo "ERROR: No config path provided."
    echo "Usage: sbatch submit_drc.sh /path/to/config.json"
    exit 1
fi

# Activate environment
module load python/3.10.10
source /gpfs/helios/home/hamza/venvs/env_dose_response/bin/activate

echo "=== Analytics Hub: DRC Timepoint Analysis ==="
echo "SLURM Job ID : $SLURM_JOB_ID"
echo "Config       : $CONFIG"
echo "Started      : $(date)"

python3 /gpfs/helios/home/hamza/projects/analytics-hub/backend/execution/hpc/jobs/run_analysis.py "$CONFIG"

EXIT_CODE=$?
echo "Finished : $(date)"
echo "Exit code: $EXIT_CODE"
exit $EXIT_CODE
