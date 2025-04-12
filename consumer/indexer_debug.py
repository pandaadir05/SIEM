#!/usr/bin/env python3
import json
import sys
import os
import time
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch, helpers
import traceback

# Add parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

def diagnose_indexer():
    print("=== SIEM Indexer Diagnostic Tool ===")
    
    # 1. Test Elasticsearch connection
    print("\n[1] Testing Elasticsearch connection...")
    try:
        es = Elasticsearch(config.ES_HOST)
        if es.ping():
            print(f"✅ Successfully connected to Elasticsearch at {config.ES_HOST}")
            # Check index exists
            if es.indices.exists(index=config.LOGS_INDEX):
                print(f"✅ The '{config.LOGS_INDEX}' index exists")
            else:
                print(f"❌ The '{config.LOGS_INDEX}' index does not exist!")
        else:
            print(f"❌ Failed to connect to Elasticsearch at {config.ES_HOST}")
            return
    except Exception as e:
        print(f"❌ Error connecting to Elasticsearch: {str(e)}")
        return
    
    # 2. Test Kafka Consumer
    print("\n[2] Testing Kafka connection...")
    try:
        consumer = KafkaConsumer(
            bootstrap_servers=config.KAFKA_BROKER,
            auto_offset_reset='earliest',
            consumer_timeout_ms=5000  # 5s timeout for testing
        )
        print(f"✅ Successfully connected to Kafka at {config.KAFKA_BROKER}")
        
        # Check if topic exists
        topics = consumer.topics()
        if config.LOGS_TOPIC in topics:
            print(f"✅ The '{config.LOGS_TOPIC}' topic exists")
        else:
            print(f"❌ The '{config.LOGS_TOPIC}' topic doesn't exist!")
            return
    except Exception as e:
        print(f"❌ Error connecting to Kafka: {str(e)}")
        return
    
    # 3. Read sample messages from Kafka
    print(f"\n[3] Reading messages from '{config.LOGS_TOPIC}'...")
    try:
        # Create a new consumer specifically for the logs topic
        topic_consumer = KafkaConsumer(
            config.LOGS_TOPIC,
            bootstrap_servers=config.KAFKA_BROKER,
            auto_offset_reset='earliest',
            consumer_timeout_ms=5000  # 5s timeout
        )
        
        messages = []
        for message in topic_consumer:
            try:
                # Decode the message
                if isinstance(message.value, bytes):
                    raw_str = message.value.decode('utf-8')
                else:
                    raw_str = message.value
                
                doc = json.loads(raw_str)
                messages.append(doc)
                
                if len(messages) >= 3:  # Just get 3 sample messages
                    break
            except Exception as e:
                print(f"❌ Error processing message: {str(e)}")
        
        if not messages:
            print("❌ No messages found in the Kafka topic!")
            return
        
        print(f"✅ Found {len(messages)} messages in Kafka")
        print(f"Sample message: {json.dumps(messages[0], indent=2)}")
        
    except Exception as e:
        print(f"❌ Error reading from Kafka: {str(e)}")
        return
    
    # 4. Test document indexing to Elasticsearch
    print("\n[4] Testing manual document indexing...")
    try:
        # Prepare documents for bulk indexing
        actions = []
        for i, doc in enumerate(messages):
            # Add @timestamp if not exists
            if '@timestamp' not in doc:
                doc['@timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            
            # Add a diagnostic field
            doc['_diagnostic'] = f"debug-test-{i}"
            
            actions.append({
                "_index": config.LOGS_INDEX,
                "_source": doc
            })
        
        # Try single document indexing first
        print("\n[4.1] Testing single document indexing...")
        try:
            single_doc = messages[0].copy()
            single_doc['_diagnostic'] = "debug-test-single"
            response = es.index(index=config.LOGS_INDEX, document=single_doc)
            print(f"✅ Single document indexed successfully with ID: {response.get('_id')}")
            
            # Clean up single document
            es.delete(index=config.LOGS_INDEX, id=response.get('_id'))
        except Exception as e:
            print(f"❌ Single document indexing failed: {str(e)}")
            print(f"Document content: {json.dumps(single_doc, indent=2)}")
        
        # Now try bulk indexing with detailed error handling
        print("\n[4.2] Testing bulk document indexing...")
        if actions:
            # Set raise_on_error to True to get detailed errors
            try:
                success, failed = helpers.bulk(
                    es, 
                    actions, 
                    stats_only=False,  # Change to get detailed response
                    raise_on_error=True,
                    raise_on_exception=True
                )
                
                print(f"✅ Successfully indexed {len(success)} test documents to '{config.LOGS_INDEX}'")
            except helpers.BulkIndexError as bulk_error:
                print(f"❌ Bulk indexing failed with {len(bulk_error.errors)} errors:")
                for i, error in enumerate(bulk_error.errors[:3]):  # Show first 3 errors
                    print(f"  Error {i+1}: {json.dumps(error, indent=2)}")
                    
                # Try more information about document format
                print("\nDocument format issues:")
                doc_sample = messages[0]
                print(f"- timestamp type: {type(doc_sample.get('timestamp')).__name__}")
                if '@timestamp' in doc_sample:
                    print(f"- @timestamp value: {doc_sample.get('@timestamp')}")
                    
                # Check if timestamp is properly formatted 
                if 'timestamp' in doc_sample:
                    ts = doc_sample.get('timestamp')
                    if isinstance(ts, (int, float)):
                        print(f"- Sample timestamp conversion: {time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(ts))}")
            except Exception as e:
                print(f"❌ Bulk indexing failed with error: {str(e)}")
                
            # Try to verify if any documents were actually indexed
            time.sleep(1)  # Give ES a moment to process
            search_query = {
                "query": {
                    "match_phrase_prefix": {
                        "_diagnostic": "debug-test"
                    }
                }
            }
            try:
                result = es.search(index=config.LOGS_INDEX, body=search_query)
                count = result["hits"]["total"]["value"]
                if count > 0:
                    print(f"✅ Found {count} documents in the index despite reported errors")
                    print("\nSample successful document:")
                    print(json.dumps(dict(result["hits"]["hits"][0]["_source"]), indent=2))
                    
                    # Cleanup test documents
                    cleanup = {
                        "query": {
                            "match_phrase_prefix": {
                                "_diagnostic": "debug-test"
                            }
                        }
                    }
                    es.delete_by_query(index=config.LOGS_INDEX, body=cleanup)
                    print("✅ Cleaned up test documents")
                else:
                    print("❌ No documents found in the index")
            except Exception as search_error:
                print(f"❌ Error checking indexed documents: {str(search_error)}")
    except Exception as e:
        print(f"❌ Error during indexing test: {str(e)}")
        print(traceback.format_exc())
    
    # 5. Check if logs index mapping is compatible with data
    print("\n[5] Checking index mapping compatibility...")
    try:
        index_mapping = es.indices.get_mapping(index=config.LOGS_INDEX)
        mapping_dict = dict(index_mapping)
        
        if "logs" in mapping_dict:
            properties = mapping_dict["logs"].get("mappings", {}).get("properties", {})
            
            print("Field mapping compatibility check:")
            for field in ["@timestamp", "timestamp", "event_type", "user", "ip", "message", "CommandLine"]:
                if field in properties:
                    print(f"✅ Field '{field}' is mapped as {properties[field].get('type')}")
                else:
                    print(f"❌ Field '{field}' is missing from mapping")
                    
            # Check for dynamic mapping settings
            if "_meta" in mapping_dict["logs"].get("mappings", {}):
                print("ℹ️ Index has custom metadata")
                
            dynamic_setting = mapping_dict["logs"].get("mappings", {}).get("dynamic", "true")
            print(f"ℹ️ Dynamic mapping is set to: {dynamic_setting}")
        else:
            print("❌ Could not find mapping properties for logs index")
    except Exception as e:
        print(f"❌ Error checking index mapping: {str(e)}")
    
    print("\n=== Diagnostic Summary ===")
    print("1. Check the indexer process logs for errors:")
    print("   - Look for 'Error during bulk indexing' messages")
    print("   - Check if the buffer is being flushed properly")
    print("   - Check for timestamp format issues")
    
    print("\n2. Common issues:")
    print("   - Timestamp field format: make sure timestamp formats match the mapping")
    print("   - Field type conflicts: ensure fields like 'ip' contain valid IP addresses")
    print("   - Document size: very large documents may be rejected")

    print("\n3. Verify your actual consumer is running with proper configuration:")
    print(f"   - ES_HOST={config.ES_HOST}")
    print(f"   - LOGS_INDEX={config.LOGS_INDEX}")
    print(f"   - KAFKA_BROKER={config.KAFKA_BROKER}")
    print(f"   - LOGS_TOPIC={config.LOGS_TOPIC}")
    
    print("\n4. Run indexer in debug mode:")
    print("   DEBUG_MODE=true python consumer/indexer.py")

    print("\n5. Try manually resetting the consumer group:")
    print(f"   kafka-consumer-groups --bootstrap-server {config.KAFKA_BROKER} --group {config.KAFKA_GROUP_ID_PREFIX}_indexer_group --reset-offsets --to-earliest --execute --topic {config.LOGS_TOPIC}")

if __name__ == "__main__":
    diagnose_indexer()
