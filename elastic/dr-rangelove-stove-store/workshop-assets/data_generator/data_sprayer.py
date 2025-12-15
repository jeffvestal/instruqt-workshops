#!/usr/bin/env python3
"""
Data Sprayer - Synthetic Observability Data Generator for Louise's EARS

Generates synthetic observability data and streams it to Elasticsearch.
Supports two modes:
- --backfill: Generate 7 days of historical data for ML training
- --live: Continuous generation with periodic anomaly injection
"""

VERSION = "2025-12-15-v4-debug-logging"  # Added detailed debugging for bulk ingestion

import argparse
import asyncio
import json
import os
import random
import sys
import threading
import time
import multiprocessing as mp
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk


# Configuration - support both naming conventions
ES_CLOUD_ID = os.environ.get("ELASTIC_CLOUD_ID") or os.environ.get("ELASTICSEARCH_URL")
ES_API_KEY = os.environ.get("ELASTIC_API_KEY") or os.environ.get("ELASTICSEARCH_APIKEY")
INDEX_NAME = "o11y-heartbeat"

# Service definitions
SERVICES = [
    "market-data-feed",
    "trade-service",
    "payment-service",
    "order-processor"
]

# Healthy baseline latencies (ms) per service
HEALTHY_LATENCIES = {
    "market-data-feed": (45, 85),    # P50: ~65ms, P99: ~85ms
    "trade-service": (80, 150),       # P50: ~115ms, P99: ~150ms
    "payment-service": (120, 300),    # P50: ~210ms, P99: ~300ms
    "order-processor": (30, 70)       # P50: ~50ms, P99: ~70ms
}

HEALTHY_MESSAGES = [
    "Request processed successfully",
    "Trade executed successfully",
    "Order validated and accepted",
    "Payment processed",
    "Market data quote updated",
    "Connection established",
    "Cache hit - serving from memory",
    "Response sent to client"
]


class DataSprayer:
    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client
        self.scenarios = self._load_scenarios()
        self.injecting_anomaly = False
        self.current_scenario = None
        
    def _load_scenarios(self) -> List[Dict[str, Any]]:
        """Load anomaly scenarios from scenarios.json"""
        try:
            with open("scenarios.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: scenarios.json not found. Using default scenarios.")
            return [
                {
                    "name": "Market Data Latency Spike",
                    "service.name": "market-data-feed",
                    "http.status_code": 200,
                    "latency_ms": 3500,
                    "log.message": "WARN: P99 latency > 3000ms",
                    "duration_seconds": 15
                }
            ]
    
    def _generate_healthy_doc(self, timestamp: datetime, service: str, business_incident_active: bool = False) -> Dict[str, Any]:
        """Generate a healthy observability document"""
        min_latency, max_latency = HEALTHY_LATENCIES[service]
        
        # Normal distribution around healthy range
        latency = random.gauss((min_latency + max_latency) / 2, (max_latency - min_latency) / 4)
        latency = max(min_latency * 0.8, min(max_latency * 1.1, latency))  # Clamp with slight variance
        
        doc = {
            "@timestamp": timestamp.isoformat(),
            "service.name": service,
            "http.status_code": random.choices([200, 201, 204], weights=[85, 10, 5])[0],
            "latency_ms": round(latency, 2),
            "log.message": random.choice(HEALTHY_MESSAGES),
            "trace.id": f"trace-{random.randint(100000, 999999)}",
            "span.id": f"span-{random.randint(100000, 999999)}"
        }
        
        # Add transaction fields for payment-service (and optionally others)
        if service == "payment-service":
            # Normal: 95% success rate, steady transaction amounts
            if business_incident_active:
                # During business incident: apply transaction_impact from scenario
                # Find the business impact scenario to get the reduction factors
                impact_scenario = next((s for s in self.scenarios if s.get("business_impact")), None)
                if impact_scenario and "transaction_impact" in impact_scenario:
                    success_rate_drop = impact_scenario["transaction_impact"]["success_rate_drop"]
                    amount_reduction = impact_scenario["transaction_impact"]["amount_reduction"]
                    
                    # Calculate reduced success rate (e.g., 0.95 * (1 - 0.6) = 0.38 = 38%)
                    success_rate = 0.95 * (1 - success_rate_drop)
                    fail_rate = (1 - success_rate) * 0.75  # 75% of failures are "failed"
                    cancel_rate = (1 - success_rate) * 0.25  # 25% of failures are "cancelled"
                    
                    transaction_status = random.choices(
                        ["success", "failed", "cancelled"], 
                        weights=[success_rate * 100, fail_rate * 100, cancel_rate * 100]
                    )[0]
                    
                    # Reduce amounts (e.g., multiply by (1 - 0.5) = 0.5 for 50% reduction)
                    amount_multiplier = (1 - amount_reduction)
                else:
                    # Fallback if scenario not found
                    transaction_status = random.choices(["success", "failed", "cancelled"], weights=[40, 45, 15])[0]
                    amount_multiplier = 0.5
                
                transaction_type = random.choice(["payment", "checkout", "order"])
                if transaction_type == "payment":
                    base_amount = random.uniform(50.0, 500.0) * amount_multiplier
                elif transaction_type == "checkout":
                    base_amount = random.uniform(25.0, 350.0) * amount_multiplier
                else:  # order
                    base_amount = random.uniform(10.0, 200.0) * amount_multiplier
            else:
                # Normal: 95% success rate
                transaction_status = random.choices(["success", "failed", "cancelled"], weights=[95, 4, 1])[0]
                transaction_type = random.choice(["payment", "checkout", "order"])
                if transaction_type == "payment":
                    base_amount = random.uniform(50.0, 500.0)
                elif transaction_type == "checkout":
                    base_amount = random.uniform(25.0, 350.0)
                else:  # order
                    base_amount = random.uniform(10.0, 200.0)
            
            doc["transaction"] = {
                "type": transaction_type,
                "amount": round(base_amount, 2),
                "status": transaction_status
            }
        
        return doc
    
    def _generate_anomaly_doc(self, timestamp: datetime, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an anomalous observability document"""
        # Add some variance to the anomaly values
        latency_variance = scenario["latency_ms"] * 0.1
        latency = scenario["latency_ms"] + random.gauss(0, latency_variance)
        
        return {
            "@timestamp": timestamp.isoformat(),
            "service.name": scenario["service.name"],
            "http.status_code": scenario["http.status_code"],
            "latency_ms": round(latency, 2),
            "log.message": scenario["log.message"],
            "trace.id": f"trace-{random.randint(100000, 999999)}",
            "span.id": f"span-{random.randint(100000, 999999)}",
            "anomaly": True  # Tag for debugging
        }
    
    def _generate_known_anomaly(self, timestamp: datetime) -> Dict[str, Any]:
        """Generate known anomaly pattern for backfill (ML training)"""
        scenario = random.choice(self.scenarios)
        return self._generate_anomaly_doc(timestamp, scenario)
    
    async def _bulk_index(self, docs: List[Dict[str, Any]]):
        """Bulk index documents to Elasticsearch"""
        actions = [
            {
                "_index": INDEX_NAME,
                "_source": doc
            }
            for doc in docs
        ]
        
        success, failed = await async_bulk(self.es_client, actions, raise_on_error=False)
        if failed:
            print(f"Warning: {len(failed)} documents failed to index")
        return success
    
    def _load_progress(self, progress_file: str) -> Dict[str, Any]:
        """Load progress from JSON file"""
        if os.path.exists(progress_file):
            try:
                with open(progress_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_progress(self, progress_file: str, progress: Dict[str, Any]):
        """Save progress to JSON file"""
        with open(progress_file, "w") as f:
            json.dump(progress, f, indent=2)
    
    @staticmethod
    def _generate_chunk_worker(chunk_id: int, start_second: int, end_second: int, start_time_iso: str, output_file: str, scenarios_path: str):
        """
        Worker function for multiprocessing - generates a chunk of time-series data.
        This runs in a separate process. Loads scenarios from file to avoid pickling issues.
        """
        # Load scenarios in worker process to avoid pickling issues
        try:
            with open(scenarios_path, "r") as f:
                scenarios = json.load(f)
        except Exception:
            # Fallback if scenarios file not found
            scenarios = []
        
        start_time = datetime.fromisoformat(start_time_iso)
        chunk_output = f"{output_file}.chunk_{chunk_id}"
        
        total = end_second - start_second
        step = max(1, total // 10)  # log every 10%
        processed = 0
        
        print(f"[Gen] Worker {chunk_id} started: seconds {start_second}-{end_second} (~{total:,} s)", flush=True)
        
        with open(chunk_output, 'w') as f:
            for i in range(start_second, end_second):
                timestamp = start_time + timedelta(seconds=i)
                
                # Generate documents for all services
                for service in SERVICES:
                    # 98% healthy, 2% anomaly
                    if random.random() < 0.98:
                        # Generate healthy doc (inline to avoid pickling issues)
                        min_latency, max_latency = HEALTHY_LATENCIES[service]
                        latency = random.gauss((min_latency + max_latency) / 2, (max_latency - min_latency) / 4)
                        latency = max(min_latency * 0.8, min(max_latency * 1.1, latency))
                        
                        doc = {
                            "@timestamp": timestamp.isoformat(),
                            "service.name": service,
                            "http.status_code": random.choices([200, 201, 204], weights=[85, 10, 5])[0],
                            "latency_ms": round(latency, 2),
                            "log.message": random.choice(HEALTHY_MESSAGES),
                            "trace.id": f"trace-{random.randint(100000, 999999)}",
                            "span.id": f"span-{random.randint(100000, 999999)}"
                        }
                        
                        # Add transaction fields for payment-service
                        if service == "payment-service":
                            transaction_status = random.choices(["success", "failed", "cancelled"], weights=[95, 4, 1])[0]
                            transaction_type = random.choice(["payment", "checkout", "order"])
                            if transaction_type == "payment":
                                base_amount = random.uniform(50.0, 500.0)
                            elif transaction_type == "checkout":
                                base_amount = random.uniform(25.0, 350.0)
                            else:  # order
                                base_amount = random.uniform(10.0, 200.0)
                            
                            doc["transaction"] = {
                                "type": transaction_type,
                                "amount": round(base_amount, 2),
                                "status": transaction_status
                            }
                    else:
                        # Generate anomaly doc
                        scenario = random.choice(scenarios) if scenarios else {
                            "name": "Market Data Latency Spike",
                            "service.name": "market-data-feed",
                            "http.status_code": 200,
                            "latency_ms": 3500,
                            "log.message": "WARN: P99 latency > 3000ms",
                            "duration_seconds": 15
                        }
                        doc = {
                            "@timestamp": timestamp.isoformat(),
                            "service.name": scenario["service.name"],
                            "http.status_code": scenario["http.status_code"],
                            "latency_ms": scenario["latency_ms"],
                            "log.message": scenario["log.message"],
                            "trace.id": f"trace-{random.randint(100000, 999999)}",
                            "span.id": f"span-{random.randint(100000, 999999)}"
                        }
                    
                    f.write(json.dumps(doc) + "\n")
        
                processed += 1
                if processed % step == 0:
                    pct = processed * 100.0 / total
                    print(f"[Gen] Worker {chunk_id}: {pct:.0f}% ({processed:,}/{total:,} s)", flush=True)
        
        print(f"[Gen] Worker {chunk_id} complete: wrote ~{total*len(SERVICES):,} docs -> {chunk_output}", flush=True)
        return chunk_output, total
    
    @staticmethod
    def _generate_chunk_worker_args(args):
        """Wrapper to unpack args tuple for imap_unordered"""
        return DataSprayer._generate_chunk_worker(*args)
    
    async def _generate_to_file_parallel(self, output_file: str, progress_file: str, days: int = 7):
        """
        Phase 1: Generate all documents to local JSONL file using multiprocessing.
        This version splits the work across CPU cores for 3-5x speedup.
        """
        print("=" * 70)
        print("PHASE 1: Generating documents to local file (PARALLEL)")
        print("=" * 70)
        
        # Calculate time range
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
        total_seconds = int((end_time - start_time).total_seconds())
        docs_per_second = len(SERVICES)
        total_docs = total_seconds * docs_per_second
        
        # Determine number of processes (leave 2 CPUs for OS/other processes)
        num_processes = max(1, mp.cpu_count() - 2)
        
        print(f"Generating {total_docs:,} documents to {output_file}")
        print(f"Time range: {start_time.isoformat()} to {end_time.isoformat()}")
        print(f"({total_seconds:,} seconds × {docs_per_second} services)")
        print(f"Using {num_processes} parallel processes (CPU count: {mp.cpu_count()})")
        
        # Calculate chunk boundaries
        chunk_size = total_seconds // num_processes
        chunks = []
        for i in range(num_processes):
            start_second = i * chunk_size
            if i == num_processes - 1:
                # Last chunk gets any remainder
                end_second = total_seconds
            else:
                end_second = (i + 1) * chunk_size
            chunks.append((i, start_second, end_second))
        
        # Start timing
        start_gen_time = time.time()
        
        # Launch parallel processes
        print(f"\n⚡ Launching {num_processes} worker processes...")
        # Get the directory where scenarios.json is located (same as script directory)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scenarios_path = os.path.join(script_dir, "scenarios.json")
        
        # Build args list for imap_unordered
        args_list = [
            (chunk_id, start_sec, end_sec, start_time.isoformat(), output_file, scenarios_path)
                 for chunk_id, start_sec, end_sec in chunks]
        
        completed_seconds = 0
        results = []
        
        # Heartbeat: prints every 15s until we flip the flag
        heartbeat_running = True
        
        def _heartbeat():
            while heartbeat_running:
                elapsed = int(time.time() - start_gen_time)
                print(f"[Gen] Heartbeat: still generating... elapsed {elapsed}s", flush=True)
                time.sleep(15)
        
        hb = threading.Thread(target=_heartbeat, daemon=True)
        hb.start()
        
        with mp.Pool(processes=num_processes) as pool:
            for chunk_output, sec_count in pool.imap_unordered(DataSprayer._generate_chunk_worker_args, args_list, chunksize=1):
                results.append((chunk_output, sec_count))
                completed_seconds += sec_count
                
                pct = (completed_seconds / total_seconds) * 100.0
                elapsed = time.time() - start_gen_time
                produced_docs = completed_seconds * len(SERVICES)
                rate = produced_docs / elapsed if elapsed > 0 else 0
                print(
                    f"[Gen] Progress: {pct:.1f}% ("
                    f"{completed_seconds:,}/{total_seconds:,} s) | "
                    f"Docs: {produced_docs:,} | Rate: {rate:,.0f} docs/sec",
                    flush=True,
                )
        
        # Stop heartbeat
        heartbeat_running = False
        hb.join(timeout=0.1)
        
        gen_time = time.time() - start_gen_time
        
        # Concatenate chunk files into final output
        print(f"\n📦 Merging {num_processes} chunk files...")
        merge_start = time.time()
        
        COPY_BUFFER = 1024 * 1024 * 10  # 10MB buffer for efficient I/O
        
        with open(output_file, 'wb') as outfile:
            for idx, (chunk_file, _) in enumerate(results, 1):
                chunk_size_mb = os.path.getsize(chunk_file) / (1024 * 1024)
                print(f"[Merge] Merging chunk {idx}/{num_processes} ({chunk_size_mb:.1f} MB)...", flush=True)
                
                # Stream copy in chunks for better I/O
                with open(chunk_file, 'rb') as infile:
                    while True:
                        data = infile.read(COPY_BUFFER)
                        if not data:
                            break
                        outfile.write(data)
                
                os.remove(chunk_file)
                elapsed = time.time() - merge_start
                print(f"[Merge] Chunk {idx}/{num_processes} complete (elapsed: {int(elapsed)}s)", flush=True)
        
        merge_time = time.time() - merge_start
        total_time = gen_time + merge_time
        
        docs_per_sec = total_docs / total_time if total_time > 0 else 0
        
        print(f"\n✅ Generation complete!")
        print(f"   Total documents: {total_docs:,}")
        print(f"   Generation time: {gen_time:.1f}s")
        print(f"   Merge time: {merge_time:.1f}s")
        print(f"   Total time: {total_time:.1f}s")
        print(f"   Rate: {docs_per_sec:,.0f} docs/sec")
        
        # Save completion status
        progress = {
            "current_second": total_seconds,
            "total_seconds": total_seconds,
            "output_file": output_file,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "completed": True
        }
        self._save_progress(progress_file, progress)
    
    async def _generate_to_file_custom(self, output_file: str, progress_file: str, days: int = 90):
        """Phase 1: Generate all documents to local JSONL file (with custom days)"""
        print("=" * 70)
        print("PHASE 1: Generating documents to local file")
        print("=" * 70)
        
        # Calculate time range
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
        total_seconds = int((end_time - start_time).total_seconds())
        docs_per_second = len(SERVICES)
        total_docs = total_seconds * docs_per_second
        
        # Load existing progress
        progress = self._load_progress(progress_file)
        start_second = progress.get("current_second", 0)
        file_mode = "a" if start_second > 0 else "w"
        
        if start_second > 0:
            print(f"Resuming generation from second {start_second:,} of {total_seconds:,}")
            print(f"Progress: {start_second / total_seconds * 100:.2f}%")
        else:
            print(f"Generating {total_docs:,} documents to {output_file}")
            print(f"Time range: {start_time.isoformat()} to {end_time.isoformat()}")
            print(f"({total_seconds:,} seconds × {docs_per_second} services)")
        
        last_update = datetime.now()
        last_count = start_second
        
        with open(output_file, file_mode) as f:
            for i in range(start_second, total_seconds):
                timestamp = start_time + timedelta(seconds=i)
                
                # Generate documents for all services
                for service in SERVICES:
                    # 98% healthy, 2% anomaly
                    if random.random() < 0.98:
                        doc = self._generate_healthy_doc(timestamp, service)
                    else:
                        doc = self._generate_known_anomaly(timestamp)
                    
                    # Write as JSON line
                    f.write(json.dumps(doc) + "\n")
                
                # Update progress every 1000 seconds (or every 5 seconds for faster feedback)
                if i % 1000 == 0 or (datetime.now() - last_update).total_seconds() >= 5:
                    progress_pct = ((i + 1) / total_seconds) * 100
                    # Calculate seconds processed in THIS interval only
                    seconds_in_interval = (i + 1) - last_count
                    elapsed = (datetime.now() - last_update).total_seconds()
                    
                    if elapsed > 0 and seconds_in_interval > 0:
                        # Rate based on this interval only, not total since resume
                        rate = seconds_in_interval / elapsed  # seconds per second (should be ~1.0 if working well)
                        remaining_seconds = total_seconds - (i + 1)
                        eta_seconds = remaining_seconds / rate if rate > 0 else 0
                        eta_str = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s" if eta_seconds > 0 else "calculating..."
                        docs_rate = seconds_in_interval * docs_per_second / elapsed
                    else:
                        eta_str = "calculating..."
                        rate = 0
                        docs_rate = 0
                    
                    print(f"\rGeneration: {progress_pct:.2f}% | "
                          f"{i+1:,}/{total_seconds:,} seconds | "
                          f"Rate: {docs_rate:.0f} docs/sec | "
                          f"ETA: {eta_str}",
                          end="", flush=True)
                    
                    # Save progress
                    progress = {
                        "current_second": i + 1,
                        "total_seconds": total_seconds,
                        "output_file": output_file,
                        "last_updated": datetime.now(timezone.utc).isoformat()
                    }
                    self._save_progress(progress_file, progress)
                    f.flush()  # Ensure data is written to disk
                    last_update = datetime.now()
                    last_count = i + 1  # Update to current position for next interval calculation
        
        print(f"\n✅ Generation complete! {total_docs:,} documents written to {output_file}")
    
    async def _generate_to_file(self, output_file: str, progress_file: str):
        """Phase 1: Generate all documents to local JSONL file"""
        # Call the parallel method with default 7 days for faster generation
        await self._generate_to_file_parallel(output_file, progress_file, days=7)
    
    async def _ingest_from_file(self, input_file: str, progress_file: str):
        """Phase 2: Bulk ingest documents from local file to Elasticsearch"""
        print("\n" + "=" * 70)
        print("PHASE 2: Bulk ingesting documents to Elasticsearch")
        print("=" * 70)
        
        if not os.path.exists(input_file):
            print(f"❌ Error: Input file {input_file} not found")
            return
        
        # Get file size
        file_size = os.path.getsize(input_file)
        file_size_mb = file_size / (1024 * 1024)
        print(f"File size: {file_size_mb:.2f} MB")
        
        # Check ES cluster health before starting bulk ingestion
        print("\n[DEBUG] Checking Elasticsearch cluster health...")
        try:
            health = await self.es_client.cluster.health(timeout="30s")
            print(f"[DEBUG] ES Cluster Status: {health['status']}")
            print(f"[DEBUG] ES Nodes: {health['number_of_nodes']} | Data Nodes: {health['number_of_data_nodes']}")
            print(f"[DEBUG] Active Shards: {health['active_shards']} | Relocating: {health['relocating_shards']} | Initializing: {health['initializing_shards']}")
            print(f"[DEBUG] Unassigned Shards: {health['unassigned_shards']} | Pending Tasks: {health['number_of_pending_tasks']}")
            if health['status'] == 'red':
                print("⚠️  WARNING: Cluster is RED - bulk ingestion may fail or be very slow!")
            elif health['status'] == 'yellow':
                print("⚠️  WARNING: Cluster is YELLOW - some replicas are not assigned")
        except Exception as e:
            print(f"[DEBUG] Failed to get cluster health: {type(e).__name__}: {e}")
        
        # Check index health
        try:
            index_exists = await self.es_client.indices.exists(index=INDEX_NAME)
            print(f"[DEBUG] Index '{INDEX_NAME}' exists: {index_exists}")
            if index_exists:
                index_stats = await self.es_client.indices.stats(index=INDEX_NAME)
                total_docs = index_stats['_all']['primaries']['docs']['count']
                store_size = index_stats['_all']['primaries']['store']['size_in_bytes'] / (1024 * 1024)
                print(f"[DEBUG] Index stats: {total_docs:,} docs, {store_size:.1f} MB")
        except Exception as e:
            print(f"[DEBUG] Failed to get index stats: {type(e).__name__}: {e}")
        
        # Test ES responsiveness with a simple bulk of 10 docs
        print("[DEBUG] Testing ES bulk responsiveness with 10 test docs...")
        test_start = time.time()
        try:
            test_docs = [
                {"_index": INDEX_NAME, "_source": {"@timestamp": datetime.now(timezone.utc).isoformat(), "service.name": "test", "test": True}}
                for _ in range(10)
            ]
            test_success, test_failed = await async_bulk(self.es_client, test_docs, raise_on_error=False)
            test_elapsed = time.time() - test_start
            print(f"[DEBUG] Test bulk completed in {test_elapsed:.2f}s - success={test_success}, failed={len(test_failed) if test_failed else 0}")
            if test_elapsed > 10:
                print(f"⚠️  WARNING: Test bulk took {test_elapsed:.1f}s - ES may be slow!")
        except Exception as e:
            test_elapsed = time.time() - test_start
            print(f"[DEBUG] Test bulk FAILED after {test_elapsed:.2f}s: {type(e).__name__}: {e}")
            print("⚠️  WARNING: ES may not be accepting bulk requests!")
        print()
        
        # Load ingestion progress
        ingest_progress_file = progress_file.replace("_progress", "_ingest_progress")
        ingest_progress = self._load_progress(ingest_progress_file)
        start_line = ingest_progress.get("last_line", 0)
        
        if start_line > 0:
            print(f"Resuming ingestion from line {start_line:,}")
        
        # Count total lines (for progress calculation)
        print("Counting total lines...")
        total_lines = 0
        with open(input_file, "r") as f:
            for _ in f:
                total_lines += 1
        
        print(f"Total documents: {total_lines:,}")
        
        # Bulk ingest settings - optimized for performance vs reliability
        batch_size = 100000  # Large batch size for good throughput
        # Use a conservative concurrency to reduce the chance of ES getting overwhelmed
        # and all batches stalling (which can cause sandbox timeouts).
        max_concurrent_batches = 2  # Process 2 batches in parallel instead of 4
        batch = []
        batch_line = 0
        indexed_total = 0
        start_time = datetime.now()
        
        print(f"Ingesting with batch size: {batch_size:,} (parallel: {max_concurrent_batches} batches)")
        print()
        
        # Helper function to ingest a single batch
        async def ingest_batch(batch_data: List[Dict], batch_num: int, start_line_num: int) -> tuple:
            """Ingest a single batch and return (success_count, failed_count, end_line_num)"""
            batch_start_time = time.time()
            try:
                print(f"[DEBUG] Batch {batch_num}: Calling async_bulk with {len(batch_data):,} docs, chunk_size={batch_size}...", flush=True)
                success, failed = await async_bulk(
                    self.es_client,
                    batch_data,
                    raise_on_error=False,
                    chunk_size=batch_size
                )
                batch_elapsed = time.time() - batch_start_time
                failed_count = len(failed) if failed else 0
                batch_rate = len(batch_data) / batch_elapsed if batch_elapsed > 0 else 0
                print(f"[DEBUG] Batch {batch_num}: async_bulk COMPLETED in {batch_elapsed:.1f}s - success={success:,}, failed={failed_count}, rate={batch_rate:.0f} docs/sec", flush=True)
                
                # Log first few errors for debugging
                if failed and len(failed) > 0:
                    print(f"[DEBUG] Batch {batch_num} first error sample: {str(failed[0])[:500]}", flush=True)
                
                end_line_num = start_line_num + len(batch_data)
                return (success, failed_count, end_line_num)
            except Exception as e:
                batch_elapsed = time.time() - batch_start_time
                print(f"\n⚠️  [DEBUG] Batch {batch_num} EXCEPTION after {batch_elapsed:.1f}s: {type(e).__name__}: {e}", flush=True)
                import traceback
                traceback.print_exc()
                return (0, len(batch_data), start_line_num + len(batch_data))
        
        # Prepare all batches first
        batches = []
        batch_num = 0
        
        with open(input_file, "r") as f:
            # Skip already processed lines
            for _ in range(start_line):
                next(f, None)
                batch_line += 1
            
            for line_num, line in enumerate(f, start=start_line):
                try:
                    doc = json.loads(line.strip())
                    batch.append({
                        "_index": INDEX_NAME,
                        "_source": doc
                    })
                    batch_line += 1
                    
                    # When batch is full, add it to batches list
                    if len(batch) >= batch_size:
                        batch_num += 1
                        batches.append((batch.copy(), batch_num, batch_line - len(batch)))
                        batch = []
                    
                except json.JSONDecodeError as e:
                    print(f"\n⚠️  Warning: Failed to parse line {line_num}: {e}")
                    continue
        
        # Add remaining documents as final batch
        if batch:
            batch_num += 1
            batches.append((batch.copy(), batch_num, batch_line - len(batch)))
            batch = []
        
        total_batches = len(batches)
        print(f"Prepared {total_batches:,} batches for parallel ingestion\n")
        
        # Process batches in parallel with semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent_batches)
        completed_batches = 0
        
        # Heartbeat: prints every 10s during ingestion
        # Use a shared dict for thread-safe progress tracking
        progress_dict = {
            "indexed_total": 0,
            "total_lines": total_lines,
            "completed_batches": 0,
            "total_batches": total_batches,
            "bailout": False,  # Signal to abort ingestion
        }
        ingest_heartbeat_running = True
        
        def _ingest_heartbeat():
            while ingest_heartbeat_running:
                elapsed = (datetime.now() - start_time).total_seconds()
                indexed = progress_dict["indexed_total"]
                total = progress_dict["total_lines"]
                completed = progress_dict.get("completed_batches", 0)
                total_b = progress_dict.get("total_batches", total_batches)
                if indexed > 0:
                    progress_pct = (indexed / total) * 100
                    rate = indexed / elapsed if elapsed > 0 else 0
                    remaining = total - indexed
                    eta_seconds = remaining / rate if rate > 0 else 0
                    eta_str = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s" if eta_seconds > 0 else "calculating..."
                    print(
                        f"[Ingest] Heartbeat: ingesting... elapsed {int(elapsed)}s, "
                        f"{progress_pct:.1f}% complete, {completed}/{total_b} batches done, ETA: {eta_str}",
                        flush=True,
                    )
                else:
                    # No batches have completed yet
                    if elapsed > 300:  # Stage 2 - Hard bailout at 5 minutes
                        print("\n" + "=" * 70, flush=True)
                        print("❌ FATAL ERROR: Data ingestion stalled", flush=True)
                        print("=" * 70, flush=True)
                        print(f"No batches completed after {int(elapsed)}s (expected ~60s)", flush=True)
                        print("This indicates an unhealthy Elasticsearch instance.", flush=True)
                        print("", flush=True)
                        print("ACTION REQUIRED: Please STOP and RESTART this sandbox.", flush=True)
                        print("=" * 70 + "\n", flush=True)
                        progress_dict["bailout"] = True
                        # Force immediate exit - don't wait for main thread
                        os._exit(1)
                    elif elapsed > 180:  # Stage 1 - Warning at 3 minutes
                        print(
                            f"⚠️  WARNING: No batches completed after {int(elapsed)}s "
                            f"(expected ~60s). Elasticsearch may be severely slow...",
                            flush=True,
                        )
                    elif elapsed > 120:
                        # After 2 minutes with no completed batches, emit a more explicit warning
                        print(
                            f"[Ingest] Heartbeat: no batches completed after {int(elapsed)}s "
                            f"({completed}/{total_b} batches done). Elasticsearch may be slow; still waiting...",
                            flush=True,
                        )
                    else:
                        print(
                            f"[Ingest] Heartbeat: ingesting... elapsed {int(elapsed)}s, starting batches...",
                            flush=True,
                        )
                time.sleep(10)
        
        hb_thread = threading.Thread(target=_ingest_heartbeat, daemon=True)
        hb_thread.start()
        
        async def ingest_with_semaphore(batch_data, batch_num, start_line_num):
            # Log when batch is queued (waiting for semaphore)
            print(f"[Batch {batch_num}/{total_batches}] Queued, waiting for semaphore (lines {start_line_num}-{start_line_num + len(batch_data)})...", flush=True)
            async with semaphore:
                # Log when semaphore acquired and batch actually starts processing
                print(f"[Batch {batch_num}/{total_batches}] ACQUIRED semaphore, sending {len(batch_data):,} docs to ES...", flush=True)
                result = await ingest_batch(batch_data, batch_num, start_line_num)
                return result
        
        # Process all batches
        tasks = [ingest_with_semaphore(batch_data, batch_num, start_line_num) 
                 for batch_data, batch_num, start_line_num in batches]
        
        # Process batches and track progress
        for task in asyncio.as_completed(tasks):
            # Check if heartbeat signaled bailout
            if progress_dict.get("bailout", False):
                ingest_heartbeat_running = False
                hb_thread.join(timeout=1)
                print("\n❌ Ingestion aborted due to poor performance", flush=True)
                os._exit(1)
            
            success, failed_count, end_line_num = await task
            completed_batches += 1
            indexed_total += success
            # Update for heartbeat
            progress_dict["indexed_total"] = indexed_total
            progress_dict["completed_batches"] = completed_batches
            
            # Stage 3 - Check first batch rate
            if completed_batches == 1:
                elapsed = (datetime.now() - start_time).total_seconds()
                first_batch_rate = success / elapsed if elapsed > 0 else 0
                if first_batch_rate < 500:  # Less than 500 docs/sec is too slow
                    print("\n" + "=" * 70, flush=True)
                    print("❌ FATAL ERROR: Ingestion rate too slow", flush=True)
                    print("=" * 70, flush=True)
                    print(f"First batch rate: {first_batch_rate:.0f} docs/sec (need >500 docs/sec)", flush=True)
                    print(f"At this rate, ingestion would take {(total_lines / first_batch_rate / 60):.0f} minutes", flush=True)
                    print("", flush=True)
                    print("ACTION REQUIRED: Please STOP and RESTART this sandbox.", flush=True)
                    print("=" * 70 + "\n", flush=True)
                    print("", flush=True)
                    # Force immediate process termination - don't wait for cleanup
                    os._exit(1)
            
            if failed_count > 0:
                print(f"\n⚠️  Warning: Batch {completed_batches}/{total_batches}: {failed_count} documents failed to index")
                
                # Update progress
                ingest_progress = {
                    "last_line": end_line_num,
                    "total_lines": total_lines,
                    "indexed_total": indexed_total,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
                self._save_progress(ingest_progress_file, ingest_progress)
            
            # Progress reporting with batch number
            progress_pct = (indexed_total / total_lines) * 100
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = indexed_total / elapsed if elapsed > 0 else 0
            remaining = total_lines - indexed_total
            eta_seconds = remaining / rate if rate > 0 else 0
            eta_str = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s" if eta_seconds > 0 else "calculating..."
            
            # Print batch completion message (new line for logs)
            print(f"[Batch {completed_batches}/{total_batches}] Indexed {indexed_total:,}/{total_lines:,} docs ({progress_pct:.2f}%) | "
                  f"Rate: {rate:.0f} docs/sec | ETA: {eta_str}")
            
            # Also update the inline progress
            print(f"\rIngestion: {progress_pct:.2f}% | "
                  f"{indexed_total:,}/{total_lines:,} docs | "
                  f"Rate: {rate:.0f} docs/sec | "
                  f"ETA: {eta_str}",
                  end="", flush=True)
                        
        # Stop heartbeat
        ingest_heartbeat_running = False
        hb_thread.join(timeout=1)
        
        # Final bailout check
        if progress_dict.get("bailout", False):
            print("\n❌ Setup aborted due to slow ingestion", flush=True)
            os._exit(1)
        
        elapsed_total = (datetime.now() - start_time).total_seconds()
        avg_rate = indexed_total / elapsed_total if elapsed_total > 0 else 0
        
        print(f"\n✅ Ingestion complete! {indexed_total:,} documents indexed")
        print(f"   Average rate: {avg_rate:.0f} docs/sec")
        print(f"   Total time: {int(elapsed_total // 60)}m {int(elapsed_total % 60)}s")
    
    async def backfill(self):
        """Generate 7 days of historical data for ML training (local-first with resume)"""
        output_file = "backfill_data.jsonl"
        progress_file = "backfill_progress.json"
        
        print("\n" + "=" * 70)
        print("BACKFILL MODE: 7 Days Historical Data Generation")
        print("=" * 70)
        print()
        print("This process has two phases:")
        print("  1. Generate all documents to local file (fast, can be paused/resumed)")
        print("  2. Bulk ingest to Elasticsearch (can be paused/resumed)")
        print()
        
        # Phase 1: Generate to file
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            await self._generate_to_file(output_file, progress_file)
        else:
            progress = self._load_progress(progress_file)
            total_seconds = progress.get("total_seconds", 0)
            current_second = progress.get("current_second", 0)
            
            if current_second < total_seconds:
                print(f"⚠️  Found incomplete generation file. Resuming...")
                await self._generate_to_file(output_file, progress_file)
            else:
                print(f"✅ Generation file already complete ({total_seconds:,} seconds)")
        
        # Phase 2: Ingest from file
        await self._ingest_from_file(output_file, progress_file)
        
        print("\n" + "=" * 70)
        print("✅ BACKFILL COMPLETE!")
        print("=" * 70)
        print("ML job can now be trained on this historical data")
        print(f"Data file: {output_file} ({os.path.getsize(output_file) / (1024**3):.2f} GB)")
    
    async def live(self):
        """Run in live mode with continuous generation and anomaly injection"""
        print("Starting live mode - generating real-time data with periodic anomalies...")
        print(f"Services: {', '.join(SERVICES)}")
        print(f"Anomaly injection: Every 60-90 seconds for 15 seconds")
        print(f"Business incident flag: /tmp/business_incident_active\n")
        
        last_anomaly_time = datetime.now(timezone.utc) - timedelta(seconds=60)
        anomaly_end_time = None
        business_incident_end_time = None
        
        while True:
            current_time = datetime.now(timezone.utc)
            
            # Check for business incident flag file
            business_incident_active = os.path.exists("/tmp/business_incident_active")
            if business_incident_active and business_incident_end_time is None:
                # Start business incident (5 minutes = 300 seconds)
                business_incident_end_time = current_time + timedelta(seconds=300)
                print(f"\n💼 BUSINESS INCIDENT ACTIVE: Payment processing degradation")
                print(f"   Service: payment-service")
                print(f"   Duration: 5 minutes\n")
            elif not business_incident_active and business_incident_end_time is not None:
                # Business incident ended
                business_incident_end_time = None
                print(f"\n✅ Business incident ended. System returning to normal.\n")
            elif business_incident_active and business_incident_end_time and current_time >= business_incident_end_time:
                # Auto-end after 5 minutes
                try:
                    os.remove("/tmp/business_incident_active")
                except:
                    pass
                business_incident_end_time = None
                print(f"\n✅ Business incident auto-ended after 5 minutes.\n")
            
            # Check if it's time to inject an anomaly (but not during business incident for payment-service)
            if not self.injecting_anomaly:
                time_since_last = (current_time - last_anomaly_time).total_seconds()
                if time_since_last >= random.randint(60, 90):
                    # Start anomaly injection (skip if business incident is active for payment-service)
                    available_scenarios = [s for s in self.scenarios if not s.get("business_impact", False)]
                    if not business_incident_active:
                        available_scenarios = self.scenarios  # Can use any scenario
                    if available_scenarios:
                        self.injecting_anomaly = True
                        self.current_scenario = random.choice(available_scenarios)
                        anomaly_end_time = current_time + timedelta(seconds=15)
                        print(f"\n🔥 INJECTING ANOMALY: {self.current_scenario['name']}")
                        print(f"   Service: {self.current_scenario['service.name']}")
                        print(f"   Duration: 15 seconds\n")
            
            # Check if anomaly should end
            if self.injecting_anomaly and current_time >= anomaly_end_time:
                self.injecting_anomaly = False
                last_anomaly_time = current_time
                print(f"\n✅ Anomaly ended. System returning to normal.\n")
            
            # Generate documents for all services
            batch = []
            for service in SERVICES:
                if self.injecting_anomaly and service == self.current_scenario["service.name"]:
                    doc = self._generate_anomaly_doc(current_time, self.current_scenario)
                else:
                    # Pass business_incident_active flag for payment-service
                    doc = self._generate_healthy_doc(current_time, service, 
                                                      business_incident_active=(business_incident_active and service == "payment-service"))
                batch.append(doc)
            
            # Index batch
            await self._bulk_index(batch)
            
            # Status update
            if business_incident_active:
                status = "💼 BUSINESS INCIDENT"
            elif self.injecting_anomaly:
                status = "🔥 ANOMALY"
            else:
                status = "✅ HEALTHY"
            print(f"[{current_time.strftime('%H:%M:%S')}] {status} - Indexed {len(batch)} documents", end='\r')
            
            # Wait 1 second
            await asyncio.sleep(1)


async def main():
    parser = argparse.ArgumentParser(description="Louise's EARS Data Sprayer - Synthetic Observability Data Generator")
    parser.add_argument("--backfill", action="store_true", help="Generate 7 days of historical data")
    parser.add_argument("--live", action="store_true", help="Run in live mode with anomaly injection (default)")
    parser.add_argument("--generate-only", action="store_true", help="Generate to local file only (no ES connection required)")
    parser.add_argument("--days", type=int, default=7, help="Number of days to generate (default: 7)")
    args = parser.parse_args()
    
    # Log version on startup
    print(f"[Data Sprayer] Version: {VERSION}")
    
    # Generate-only mode doesn't need ES credentials
    if args.generate_only:
        output_file = "backfill_data.jsonl"
        progress_file = "backfill_progress.json"
        
        print("\n" + "=" * 70)
        print(f"GENERATE-ONLY MODE: {args.days} Days Historical Data Generation")
        print("=" * 70)
        print("Generating to local file only - no Elasticsearch connection required")
        print()
        
        # Create a minimal sprayer for file generation
        sprayer = DataSprayer(None)  # No ES client needed
        
        # Generate to file using parallel method for speed
        await sprayer._generate_to_file_parallel(output_file, progress_file, args.days)
        
        print("\n" + "=" * 70)
        print("✅ GENERATION COMPLETE!")
        print("=" * 70)
        print(f"Data file: {output_file}")
        print("To ingest to Elasticsearch, run with --backfill mode")
        return
    
    # Validate environment variables for backfill/live modes
    if not ES_CLOUD_ID or not ES_API_KEY:
        print("Error: ELASTIC_CLOUD_ID/ELASTICSEARCH_URL and ELASTIC_API_KEY/ELASTICSEARCH_APIKEY environment variables must be set")
        sys.exit(1)
    
    # Connect to Elasticsearch
    print("Connecting to Elasticsearch...")
    print(f"[DEBUG] ES_CLOUD_ID value: {ES_CLOUD_ID}")
    print(f"[DEBUG] ES_CLOUD_ID type: {type(ES_CLOUD_ID)}")
    print(f"[DEBUG] ES_CLOUD_ID starts with http://: {ES_CLOUD_ID.startswith('http://') if ES_CLOUD_ID else False}")
    print(f"[DEBUG] ES_CLOUD_ID starts with https://: {ES_CLOUD_ID.startswith('https://') if ES_CLOUD_ID else False}")
    
    # Support both Cloud ID (traditional) and URL (serverless/local)
    es_client = None
    try:
        if ES_CLOUD_ID and (ES_CLOUD_ID.startswith("https://") or ES_CLOUD_ID.startswith("http://")):
            # URL-based connection (http:// or https://)
            print(f"[DEBUG] Using URL-based connection: {ES_CLOUD_ID}")
            es_client = AsyncElasticsearch(
                hosts=[ES_CLOUD_ID],
                api_key=ES_API_KEY,
                request_timeout=300,  # Increased for large parallel batches
                max_retries=3,
                retry_on_timeout=True
            )
        else:
            # Traditional Cloud ID connection
            print(f"[DEBUG] Using Cloud ID-based connection")
            es_client = AsyncElasticsearch(
                cloud_id=ES_CLOUD_ID,
                api_key=ES_API_KEY,
                request_timeout=300,  # Increased for large parallel batches
                max_retries=3,
                retry_on_timeout=True
            )
        print("[DEBUG] Elasticsearch client created successfully")
    except Exception as e:
        print("\n" + "=" * 70)
        print("ERROR: Failed to create Elasticsearch client")
        print("=" * 70)
        print(f"ES_CLOUD_ID: {ES_CLOUD_ID}")
        print(f"ES_API_KEY: {'*' * (len(ES_API_KEY) - 4) + ES_API_KEY[-4:] if ES_API_KEY else '(not set)'}")
        print(f"\nException type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        sys.exit(1)
    
    try:
        # Verify connection
        info = await es_client.info()
        print(f"Connected to Elasticsearch {info['version']['number']}")
        
        # Initialize data sprayer
        sprayer = DataSprayer(es_client)
        
        # Run appropriate mode
        if args.backfill:
            await sprayer.backfill()
        else:
            # Default to live mode
            await sprayer.live()
    
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
    except Exception as e:
        print("\n" + "=" * 70)
        print("ERROR: Exception occurred during data generation")
        print("=" * 70)
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        sys.exit(1)
    finally:
        if es_client:
            await es_client.close()
            print("Connection closed")


if __name__ == "__main__":
    asyncio.run(main())



