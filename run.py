import sys
from pathlib import Path

# Add the project directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from web3_data_aggregator.cli import main

if __name__ == "__main__":
    main()