# Etsy Tool

(c) 2020 Shaun Rasmusen

---

## Description

A helper tool for retreiving information from the Etsy API that is otherwise
more difficult to access through their site or only exposed programmatically.

---

## How to Run

First, install [requests](https://pypi.org/project/requests/) using `pip`, then
run: `ETSY_API_KEY={api_key} python3 main.py` substituting `{api_key}` for your
Etsy API key. Your API key may also be saved to `.api_key` in the root directory.

---

## Packaging for Mac

First, install [py2app](https://pypi.org/project/py2app/) and [requests](https://pypi.org/project/requests/)
using `pip`, then run `ETSY_API_KEY={api_key} make package-app` substituting 
`{api_key}` for your Etsy API key.

This will package a standalone app for Etsy Tool and save it under `dist/`.

NOTE: This app is not cross-version compatible. If packaged on MacOS 10.14, it
likely will only work on that version.
