Python 3.8 intended.

# Worker configuration
Configuration is via `config.json`.
Available options are documented here:
* `ecm_path` - path to a GMP-ECM binary (required)
* `cado_path` - path to a CADO-NFS script (required)
* `ecm_procs` - number of parallel ECM instances to run (default: 1)
* `min_digits` - minimum composite size to get from FactorDB (default: 79)
    * recommend at least 70, because FactorDB quickly factors most smaller numbers
* `number` - number of composites to get per FactorDB request (default: 50)
* `offset` - skip first `n` composites in FactorDB listing (default: 0)
    * helpful to avoid duplicating work

# Code
* `factordb.py` contains methods for talking to factordb
* `factoring.py` contains methods for running factorization
* `worker.py` gets work and runs factorization
