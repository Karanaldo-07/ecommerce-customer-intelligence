"""Run the complete initial analytics pipeline."""
from ecommerce_intel.pipeline import run_pipeline
import json

if __name__ == "__main__":
    print(json.dumps(run_pipeline(), indent=2))
