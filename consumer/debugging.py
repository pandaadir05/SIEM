#!/usr/bin/env python3
import json
from elasticsearch import Elasticsearch
import sys

ES_HOST = "http://localhost:9200"

def debug_indices():
    print(f"Connecting to Elasticsearch at {ES_HOST}...")
    es = Elasticsearch(ES_HOST)
    
    # Verify connection
    if not es.ping():
        print("Failed to connect to Elasticsearch!")
        return
    
    print("Successfully connected to Elasticsearch")
    
    # Get all indices
    try:
        indices = es.indices.get_alias(index="*")
        print("\nAvailable indices:", list(indices.keys()))
    except Exception as e:
        print(f"Error getting indices: {str(e)}")
        return
    
    # Check logs index specifically
    if "logs" in indices:
        print("\n==== LOGS INDEX ====")
        try:
            # Convert response to dict to make it JSON serializable
            logs_mapping = es.indices.get_mapping(index="logs")
            logs_mapping_dict = dict(logs_mapping)
            print("Logs index mapping:", json.dumps(logs_mapping_dict, indent=2))
            
            # Check for timestamp field
            if "logs" in logs_mapping_dict:
                properties = logs_mapping_dict["logs"].get("mappings", {}).get("properties", {})
                if "@timestamp" in properties:
                    print("\n@timestamp field exists with type:", properties["@timestamp"].get("type"))
                else:
                    print("\nWARNING: @timestamp field missing in mapping!")
            
            # Count documents
            logs_count = es.count(index="logs")
            print("\nLogs count:", logs_count["count"])
            
            # Sample documents if any exist
            if logs_count["count"] > 0:
                sample = es.search(index="logs", size=1)
                print("\nSample log document:")
                print(json.dumps(dict(sample["hits"]["hits"][0]["_source"]), indent=2))
            else:
                print("\nNo documents found in logs index")
                
        except Exception as e:
            print(f"Error analyzing logs index: {str(e)}")
    else:
        print("\nWARNING: logs index does not exist!")

    # Check alerts index 
    if "alerts" in indices:
        print("\n==== ALERTS INDEX ====")
        try:
            alerts_count = es.count(index="alerts")
            print("Alerts count:", alerts_count["count"])
            
            if alerts_count["count"] > 0:
                sample = es.search(index="alerts", size=1)
                print("\nSample alert document:")
                print(json.dumps(dict(sample["hits"]["hits"][0]["_source"]), indent=2))
            else:
                print("\nNo documents found in alerts index")
                
        except Exception as e:
            print(f"Error analyzing alerts index: {str(e)}")
    else:
        print("\nWARNING: alerts index does not exist!")

if __name__ == "__main__":
    try:
        debug_indices()
    except Exception as e:
        print(f"Unhandled exception: {str(e)}")
        sys.exit(1)
