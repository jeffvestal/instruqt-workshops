#!/usr/bin/env python3
"""
Minimal setup script for workshop - creates o11y-heartbeat index with proper mappings
"""
import os
import sys
from elasticsearch import Elasticsearch

# Support both naming conventions
ES_URL = os.environ.get("ELASTIC_CLOUD_ID") or os.environ.get("ELASTICSEARCH_URL")
ES_API_KEY = os.environ.get("ELASTIC_API_KEY") or os.environ.get("ELASTICSEARCH_APIKEY")

if not ES_URL or not ES_API_KEY:
    print("ERROR: ELASTIC_CLOUD_ID/ELASTICSEARCH_URL and ELASTIC_API_KEY/ELASTICSEARCH_APIKEY must be set")
    sys.exit(1)

def main():
    print(f"[Setup] Connecting to {ES_URL}")
    
    # Connect to Elasticsearch
    if ES_URL.startswith("https://") or ES_URL.startswith("http://"):
        # URL-based connection
        es = Elasticsearch(
            hosts=[ES_URL],
            api_key=ES_API_KEY,
            request_timeout=60
        )
    else:
        # Cloud ID connection
        es = Elasticsearch(
            cloud_id=ES_URL,
            api_key=ES_API_KEY,
            request_timeout=60
        )
    
    # Test connection
    try:
        info = es.info()
        print(f"[Setup] ✓ Connected to Elasticsearch {info['version']['number']}")
    except Exception as e:
        print(f"[Setup] ERROR: Failed to connect to Elasticsearch: {e}")
        sys.exit(1)
    
    # Create index with mappings
    index_name = "o11y-heartbeat"
    
    if es.indices.exists(index=index_name):
        print(f"[Setup] Index {index_name} already exists, skipping creation")
        return
    
    print(f"[Setup] Creating index: {index_name}")
    
    try:
        es.indices.create(
            index=index_name,
            body={
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "service.name": {"type": "keyword"},
                        "latency_ms": {"type": "long"},
                        "http.status_code": {"type": "integer"},
                        "log.message": {"type": "text"},
                        "trace.id": {"type": "keyword"},
                        "span.id": {"type": "keyword"}
                    }
                }
            }
        )
        print(f"[Setup] ✓ Index created: {index_name}")
    except Exception as e:
        print(f"[Setup] ERROR: Failed to create index: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
