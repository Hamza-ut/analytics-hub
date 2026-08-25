from config.celery import app


@app.task(bind=True)
def run_strainqc_task(self, project_id):
    # TODO: implement HPC job submission via hpc/ module
    # Steps:
    #   1. Load StrainQCConfig for this project_id
    #   2. Download reads files + reference file from uploads
    #   3. Submit SLURM job via paramiko (hpc/ module)
    #   4. Poll until complete
    #   5. Download results.json, coverage.tsv
    #   6. Parse and store in StrainQCResult
    #   7. Update project status to COMPLETED or FAILED
    pass
