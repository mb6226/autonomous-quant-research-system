#!/usr/bin/env python3
from app.data.providers.dukascopy.downloader import DukascopyDownloader

def main():
    d = DukascopyDownloader(symbol="EURUSD")
    # adjust years as needed
    d.download_range(start_year=2018, end_year=2025)

if __name__ == '__main__':
    main()
