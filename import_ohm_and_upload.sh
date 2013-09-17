#!/bin/sh -ex
python3 convert_buddy.py < ohm.bl | ./upload_and_create_new_sample_ledger.sh
