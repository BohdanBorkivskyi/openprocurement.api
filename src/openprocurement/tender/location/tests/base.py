import json
import os

here = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(here, "data/tender_data.json")) as _in:
    test_tender_data = json.load(_in)
