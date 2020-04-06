from pathlib import Path
import os

file = "cloud_data.db"
if os.path.exists(file):
        os.remove(file)


