#!/usr/bin/env python3
import os
import sys
import argparse
import csv
import json

from dotenv import load_dotenv
import requests

# === Load configuration from .env ===
load_dotenv("../.env")
DEFAULT_URL   = os.getenv("PAPERLESS_URL", "http://localhost:8000")
DEFAULT_TOKEN = os.getenv("PAPERLESS_TOKEN")

def get_mapping(session, base_url, endpoint, name_key="name"):
    """
    Generic ID→name/title mapping for endpoints like tags or document_types.
    """
    mapping = {}
    url = f"{base_url.rstrip('/')}/api/{endpoint}/?page_size=100"
    while url:
        r = session.get(url)
        r.raise_for_status()
        data = r.json()
        for obj in data.get("results", []):
            mapping[obj["id"]] = obj.get(name_key, "")
        url = data.get("next")
    return mapping


def fetch_all_documents(session, base_url):
    """
    Fetch all documents (paginated) from /api/documents/
    """
    docs = []
    url = f"{base_url.rstrip('/')}/api/documents/?page_size=100"
    while url:
        r = session.get(url)
        r.raise_for_status()
        batch = r.json()
        docs.extend(batch.get("results", []))
        url = batch.get("next")
    return docs


def main():
    parser = argparse.ArgumentParser(
        description="Export all Paperless-ngx documents (with tags, types & custom fields) to CSV or JSON."
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_URL,
        help=f"Base URL of your Paperless-ngx instance (env PAPERLESS_URL), default: {DEFAULT_URL}"
    )
    parser.add_argument(
        "--api-token",
        default=DEFAULT_TOKEN,
        help="API token for Paperless-ngx (env PAPERLESS_TOKEN)"
    )
    parser.add_argument(
        "--format", choices=("csv", "json"), default="csv",
        help="Output format (default: csv)"
    )
    parser.add_argument(
        "--output",
        help="Output file (defaults to paperless_export.csv or .json in cwd)"
    )
    args = parser.parse_args()

    if not args.api_token:
        print("Error: API token must be provided via --api-token or PAPERLESS_TOKEN in .env", file=sys.stderr)
        sys.exit(1)

    session = requests.Session()
    session.headers.update({"Authorization": f"Token {args.api_token}"})

    # build mappings for tags and document types
    tag_map  = get_mapping(session, args.api_url, "tags", name_key="name")
    type_map = get_mapping(session, args.api_url, "document_types", name_key="name")

    # fetch all documents
    docs = fetch_all_documents(session, args.api_url)
    if not docs:
        print("No documents found.", file=sys.stderr)
        sys.exit(1)

    # collect custom-field IDs in use
    cf_ids = {cf.get("field") for d in docs for cf in d.get("custom_fields", []) if cf.get("field") is not None}

    # fetch each custom-field definition, with warnings on errors
    cf_def_map = {}
    
    for cf_id in cf_ids:
        url = f"{args.api_url.rstrip('/')}/api/custom_fields/{cf_id}/"
        r = session.get(url)
        if not r.ok:
            print(f"Warning: couldn't fetch definition for CF #{cf_id} (HTTP {r.status_code})", file=sys.stderr)
            cf_def_map[cf_id] = ""
            continue
        # only attempt JSON if content-type indicates JSON
        content_type = r.headers.get('Content-Type', '')
        print(cf_def_map, cf_id)
        if 'application/json' not in content_type:
            
            print(f"Warning: non-JSON response for CF #{cf_id} (Content-Type: {content_type})", file=sys.stderr)
            cf_def_map[cf_id] = ""
            continue
        try:
            data = r.json()
            cf_def_map[cf_id] = data.get("title", "")
        except ValueError:
            print(f"Warning: invalid JSON for CF #{cf_id}: {r.text[:200]!r}", file=sys.stderr)
            cf_def_map[cf_id] = ""

    # prepare rows
    all_cf_titles = set(cf_def_map.values()) - {""}
    rows = []
    for d in docs:
        row = {}
        skip = {"tags", "document_type", "custom_fields", "content"}
        for k, v in d.items():
            if k not in skip:
                row[k] = v

        # map document_type and tags
        row["document_type"] = type_map.get(d.get("document_type"), "")
        tag_names = [tag_map.get(tid, str(tid)) for tid in d.get("tags", [])]
        row["tags"] = ";".join(tag_names)

        # flatten custom fields
        cf_vals = {}
        for cf in d.get("custom_fields", []):
            fid = cf.get("field")
            title = cf_def_map.get(fid, "")
            if title:
                cf_vals[title] = cf.get("value")
        for title in all_cf_titles:
            row[title] = cf_vals.get(title)

        rows.append(row)

    # write output
    default_out = f"./paperless_export.{args.format}"
    out_path = args.output or default_out
    if args.format == "json":
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2, default=str)
    else:
        headers = list(rows[0].keys())
        with open(out_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    print(f"✅ Exported {len(rows)} documents to {out_path}")

if __name__ == "__main__":
    main()
