import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.insert_data import insert_characters

if __name__ == "__main__":
    asyncio.run(insert_characters())
