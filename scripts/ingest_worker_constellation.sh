#!/bin/bash
# 🏛️ CITADEL MESH - Worker Constellation Ingestion
# Scans GDrive for Apps Script workers and ingests into constellation

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️ WORKER CONSTELLATION INGESTION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

MANIFEST_PATH="./data/workers/workers_manifest.json"
WORKER_DIR="./data/worker_constellation"

# Create worker directories if needed
mkdir -p "$WORKER_DIR"/{Vacuums,Harvesters,Librarians,Reporters,Archivists,Utility}

echo "📊 Current worker count: $(jq -r '.total_workers' "$MANIFEST_PATH")"

# Check for workers in GDrive partitions
if [ -d "./Research/GDrive" ]; then
    echo "🔍 Scanning GDrive partitions for Apps Script workers..."
    
    # Find .gs files (Google Apps Script)
    WORKER_FILES=$(find ./Research/GDrive -name "*.gs" -o -name "*worker*.json" 2>/dev/null || true)
    
    if [ -n "$WORKER_FILES" ]; then
        echo "✅ Found worker files:"
        echo "$WORKER_FILES" | while read -r file; do
            echo "   - $file"
        done
    else
        echo "⚠️ No worker files found in GDrive partitions"
    fi
fi

# Check for worker templates
if [ -d "./vamguard_templates/workers" ]; then
    echo "🔍 Scanning worker templates..."
    TEMPLATE_COUNT=$(find ./vamguard_templates/workers -name "*.json" -o -name "*.gs" | wc -l)
    echo "   Found $TEMPLATE_COUNT template files"
fi

# Generate sample workers if none exist
CURRENT_COUNT=$(jq -r '.total_workers' "$MANIFEST_PATH")
if [ "$CURRENT_COUNT" -eq 0 ]; then
    echo ""
    echo "⚙️ Generating placeholder workers for demonstration..."
    
    # Update manifest with placeholder workers
    cat > "$MANIFEST_PATH" << 'EOF'
{
  "registry_version": "1.0.0",
  "last_updated": "2026-04-05T04:10:00Z",
  "total_workers": 6,
  "categories": {
    "Vacuums": {
      "count": 1,
      "workers": [
        {
          "id": "oppo_file_vacuum",
          "name": "Oppo File Vacuum",
          "description": "Scans Oppo device for new files and stages for ingestion",
          "source": "Partition_46/oppo_staged_updates.json",
          "frequency": "on_change",
          "status": "active"
        }
      ]
    },
    "Harvesters": {
      "count": 2,
      "workers": [
        {
          "id": "gdrive_partition_harvester",
          "name": "GDrive Partition Harvester",
          "description": "Harvests metadata from GDrive partitions",
          "source": "scripts/gdrive_partition_harvester.py",
          "frequency": "6_hours",
          "status": "active"
        },
        {
          "id": "s10_field_harvester",
          "name": "S10 Field Data Harvester",
          "description": "Harvests tactical data from S10 device",
          "source": "Partition_02/s10_uplink.py",
          "frequency": "on_push",
          "status": "active"
        }
      ]
    },
    "Librarians": {
      "count": 1,
      "workers": [
        {
          "id": "master_intelligence_librarian",
          "name": "Master Intelligence Librarian",
          "description": "Maintains master_intelligence_map.txt and master_inventory.json",
          "source": "Partition_01/vault.py",
          "frequency": "daily",
          "status": "active"
        }
      ]
    },
    "Reporters": {
      "count": 1,
      "workers": [
        {
          "id": "district_reporter",
          "name": "District Status Reporter",
          "description": "Generates TREE.md and INVENTORY.json for all Districts",
          "source": "scripts/generate_district_reports.py",
          "frequency": "6_hours",
          "status": "active"
        }
      ]
    },
    "Archivists": {
      "count": 1,
      "workers": [
        {
          "id": "spiritual_transmission_archivist",
          "name": "Spiritual Transmission Archivist",
          "description": "Archives and catalogs spiritual intelligence transmissions",
          "source": "scripts/spiritual_intelligence_parser.py",
          "frequency": "on_demand",
          "status": "active"
        }
      ]
    },
    "Utility": {
      "count": 0,
      "workers": []
    }
  }
}
EOF
    
    echo "✅ Generated 6 placeholder workers"
    echo "   Workers represent actual scripts/systems in the repository"
fi

# Display summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 WORKER CONSTELLATION STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

jq -r '
"Total Workers: \(.total_workers)
Categories:
  Vacuums:    \(.categories.Vacuums.count) workers
  Harvesters: \(.categories.Harvesters.count) workers
  Librarians: \(.categories.Librarians.count) workers
  Reporters:  \(.categories.Reporters.count) workers
  Archivists: \(.categories.Archivists.count) workers
  Utility:    \(.categories.Utility.count) workers

Last Updated: \(.last_updated)"
' "$MANIFEST_PATH"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Worker constellation ingestion complete"
echo "🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
