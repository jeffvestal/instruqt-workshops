#!/bin/bash
# test_data_generator.sh - Test data generation performance

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Data Generator Performance Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test configurations
DAYS_TO_TEST=(7 30 60 90)
RESULTS_FILE="test_results_$(date +%Y%m%d_%H%M%S).txt"

echo "Test configurations: ${DAYS_TO_TEST[@]} days" | tee -a "$RESULTS_FILE"
echo "Output: $RESULTS_FILE" | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"

# Function to clean up files
cleanup_files() {
  echo -e "${YELLOW}Cleaning up previous test files...${NC}"
  rm -f data_generator/backfill_data.jsonl
  rm -f data_generator/backfill_progress.json
  rm -f data_generator/backfill_ingest_progress.json
}

# Function to modify data_sprayer.py to use specific days
modify_days() {
  local days=$1
  echo -e "${YELLOW}Modifying data_sprayer.py to generate ${days} days...${NC}"
  
  # Create backup if doesn't exist
  if [[ ! -f data_generator/data_sprayer.py.backup ]]; then
    cp data_generator/data_sprayer.py data_generator/data_sprayer.py.backup
  fi
  
  # Modify line 160 (timedelta days)
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/timedelta(days=[0-9]*)/timedelta(days=${days})/" data_generator/data_sprayer.py
  else
    # Linux
    sed -i "s/timedelta(days=[0-9]*)/timedelta(days=${days})/" data_generator/data_sprayer.py
  fi
  
  # Verify change
  if grep -q "timedelta(days=${days})" data_generator/data_sprayer.py; then
    echo -e "${GREEN}✓ Set to ${days} days${NC}"
  else
    echo -e "${YELLOW}⚠ Could not verify change${NC}"
  fi
}

# Function to restore original
restore_original() {
  if [[ -f data_generator/data_sprayer.py.backup ]]; then
    mv data_generator/data_sprayer.py.backup data_generator/data_sprayer.py
    echo -e "${GREEN}✓ Restored original data_sprayer.py${NC}"
  fi
}

# Trap to ensure cleanup on exit
trap restore_original EXIT

echo -e "${BLUE}Starting tests (generation only - no ES ingestion)...${NC}\n"

# Run tests for each configuration
for days in "${DAYS_TO_TEST[@]}"; do
  echo "" | tee -a "$RESULTS_FILE"
  echo -e "${BLUE}========================================${NC}" | tee -a "$RESULTS_FILE"
  echo -e "${BLUE}TEST: ${days} days${NC}" | tee -a "$RESULTS_FILE"
  echo -e "${BLUE}========================================${NC}" | tee -a "$RESULTS_FILE"
  
  # Clean up previous run
  cleanup_files
  
  # Modify script for this test
  modify_days $days
  
  # Calculate expected documents
  SECONDS_IN_DAYS=$((days * 86400))
  SERVICES=4
  EXPECTED_DOCS=$((SECONDS_IN_DAYS * SERVICES))
  
  echo "Expected documents: $(printf "%'d" $EXPECTED_DOCS)" | tee -a "$RESULTS_FILE"
  echo "" | tee -a "$RESULTS_FILE"
  
  # Run generation only
  echo -e "${GREEN}Running generation (local file only)...${NC}"
  START_TIME=$(date +%s)
  
  cd data_generator
  python3 data_sprayer.py --generate-only --days $days 2>&1 | tee -a "../$RESULTS_FILE"
  cd ..
  
  END_TIME=$(date +%s)
  ELAPSED=$((END_TIME - START_TIME))
  
  # Check if file was created
  if [[ -f data_generator/backfill_data.jsonl ]]; then
    FILE_SIZE=$(du -h data_generator/backfill_data.jsonl | cut -f1)
    LINE_COUNT=$(wc -l < data_generator/backfill_data.jsonl)
    DOCS_PER_SEC=$((LINE_COUNT / ELAPSED))
    
    echo "" | tee -a "$RESULTS_FILE"
    echo -e "${GREEN}Results:${NC}" | tee -a "$RESULTS_FILE"
    echo "  Time: ${ELAPSED}s" | tee -a "$RESULTS_FILE"
    echo "  File size: ${FILE_SIZE}" | tee -a "$RESULTS_FILE"
    echo "  Documents: $(printf "%'d" $LINE_COUNT)" | tee -a "$RESULTS_FILE"
    echo "  Rate: $(printf "%'d" $DOCS_PER_SEC) docs/sec" | tee -a "$RESULTS_FILE"
  else
    echo -e "${YELLOW}⚠ backfill_data.jsonl not created${NC}" | tee -a "$RESULTS_FILE"
  fi
done

# Final cleanup
cleanup_files

echo "" | tee -a "$RESULTS_FILE"
echo -e "${BLUE}========================================${NC}" | tee -a "$RESULTS_FILE"
echo -e "${BLUE}All tests complete!${NC}" | tee -a "$RESULTS_FILE"
echo -e "${BLUE}========================================${NC}" | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"
echo "Results saved to: $RESULTS_FILE"

# Show summary
echo ""
echo -e "${GREEN}Summary:${NC}"
grep -E "TEST:|Time:|Rate:" "$RESULTS_FILE" | sed 's/\x1b\[[0-9;]*m//g' || true

