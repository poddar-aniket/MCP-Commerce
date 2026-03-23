@echo off
python -m pip install "datasets>=2.16.1" --upgrade --user
python test_us_markets.py > output.txt 2>&1
echo Done > done.txt
