import os
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from recommendation_service import create_app

app = create_app()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    app.run(host="0.0.0.0", port=port, debug=True)