#!/usr/bin/env python3
"""
Build a JSON listings file from FlexMLS CSV data for the website.
Run daily after the MLS scraper completes.
"""
import csv, json, os, sys
sys.path.insert(0, "/home/empathetic/.openclaw/workspace")
from vesta_utils import listing_slug as _listing_slug, zip_to_city as _zip_to_city

WORKSPACE = "/home/empathetic/.openclaw/workspace"
OUTPUT = "/home/empathetic/eliterealty.homes/api/listings.json"

def load_csv(path, prop_type):
    listings = []
    if not os.path.exists(path):
        return listings
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if row.get('Status', '').strip() != 'A':
                    continue
                price = float(row.get('List Price', 0) or 0)
                if price <= 0:
                    continue
                address = f"{row.get('Street #', '')} {row.get('Street Name', '')} {row.get('Suffix', '')}".strip()
                city    = row.get('City', '')
                zipcode = row.get('Zip Code', '').strip()
                # Enrich ZIP with city/county data (cached locally — no API calls)
                zip_info = _zip_to_city(zipcode)
                listings.append({
                    "id":      row.get('List Number', ''),
                    "slug":    _listing_slug(f"{address} {city} MI {zipcode}"),
                    "type":    prop_type,
                    "price":   int(price),
                    "address": address,
                    "city":    city or zip_info.get("city", ""),
                    "zip":     zipcode,
                    "county":  zip_info.get("county", ""),
                    "beds":    int(float(row.get('Total Bedrooms', 0) or 0)),
                    "baths":   float(row.get('Total Baths', 0) or 0),
                    "sqft":    int(float(row.get('SqFt Above Grade', 0) or 0)),
                    "acres":   float(row.get('Lot Acres', 0) or 0),
                    "dom":     int(float(row.get('Days on Market', 0) or 0)),
                    "status":  row.get('Status', ''),
                    "school":  row.get('School District', ''),
                    "remarks":   (row.get('Public Remarks', '') or '')[:250],
                    "agent":     row.get('Listing Agent', ''),
                    "agency":    row.get('Agency Name', ''),
                    "year_built": row.get('Year Built', '').strip() or None,
                    "garage":    row.get('Garage Y/N', '').strip().upper() == 'Y',
                    "new_const": row.get('New Construction', '').strip().upper() == 'Y',
                })
            except (ValueError, TypeError):
                continue
    return listings

sfh = load_csv(os.path.join(WORKSPACE, "flexmls-sfh.csv"), "Residential")
mfh = load_csv(os.path.join(WORKSPACE, "flexmls-mfh.csv"), "Multi-Family")
land = load_csv(os.path.join(WORKSPACE, "flexmls-land.csv"), "Land")

all_listings = sfh + mfh + land
all_listings.sort(key=lambda x: x['dom'])

# Determine freshness timestamp from whichever CSV exists
_sfh_csv = os.path.join(WORKSPACE, "flexmls-sfh.csv")
_mfh_csv = os.path.join(WORKSPACE, "flexmls-mfh.csv")
_updated_ts = None
for _csv_path in (_sfh_csv, _mfh_csv):
    if os.path.exists(_csv_path):
        _updated_ts = os.path.getmtime(_csv_path)
        break

from datetime import datetime, timezone
_updated_iso = (
    datetime.fromtimestamp(_updated_ts, tz=timezone.utc).isoformat()
    if _updated_ts else ""
)

output = {
    "updated": _updated_iso,
    "total": len(all_listings),
    "sfh": len(sfh),
    "mfh": len(mfh),
    "land": len(land),
    "listings": all_listings,
}

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False)

print(f"Built {len(all_listings)} listings → {OUTPUT}")
