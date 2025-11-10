# Data Generator Performance Comparison

## Multiprocessing Optimization Results

### Before (Single-threaded)
| Duration | Time | Rate | Documents |
|----------|------|------|-----------|
| 7 days   | 11s  | ~220K docs/sec | 2.4M |
| 30 days  | 46s  | ~225K docs/sec | 10.4M |
| 60 days  | 93s  | ~223K docs/sec | 20.7M |
| 90 days  | 144s (2m 24s) | ~216K docs/sec | 31.1M |

### After (Multiprocessing - 14 cores)
| Duration | Time | Rate | Documents | Speedup |
|----------|------|------|-----------|---------|
| 7 days   | 2s   | **1.47M docs/sec** | 2.4M | **5.5x faster** ⚡ |
| 30 days  | 6s   | **1.75M docs/sec** | 10.4M | **7.7x faster** ⚡⚡ |
| 60 days  | 11s  | **1.86M docs/sec** | 20.7M | **8.5x faster** ⚡⚡⚡ |
| 90 days  | 17s  | **1.91M docs/sec** | 31.1M | **8.5x faster** 🚀 |

## Key Improvements

### Speed
- **Average speedup: 7.5x faster**
- **Peak throughput: 1.91M docs/sec** (vs 220K before)
- **90 days now takes 17 seconds** instead of 2.5 minutes

### Implementation
- Uses Python `multiprocessing` to bypass GIL
- Splits time range into chunks (one per CPU core)
- Each process generates its chunk independently
- Merges chunk files at the end
- Scales automatically based on CPU count (capped at 16 cores)

### File Sizes
- 7 days: 533 MB
- 30 days: 2.2 GB
- 60 days: 4.5 GB
- 90 days: 6.7 GB

## Workshop Impact

With these speeds, we can now:
1. **Generate 90 days in 17 seconds** - fast enough for live workshop setup
2. **Skip snapshot creation** - generation is faster than snapshot restore
3. **Simplify setup scripts** - just run the generator directly
4. **Easy testing** - quick iteration during development

## Technical Details

### Worker Function
Each worker process:
- Generates a time-range chunk independently
- Writes to a separate temp file
- Uses inline generation logic (no pickling of class methods)
- Returns chunk file path and doc count

### Merge Phase
- Concatenates all chunk files in order
- Uses binary mode for speed
- Cleans up temp files
- Very fast (typically <15% of total time)

### Data Quality
- **No change to data quality** - same Gaussian distributions
- **Same anomaly injection rate** (2% during backfill)
- **Same service baselines and patterns**
- Only optimization is parallel generation

## Conclusion

**Multiprocessing provides 7-8x speedup** with minimal code complexity and no compromise on data quality. Perfect for workshop deployment! 🎯
