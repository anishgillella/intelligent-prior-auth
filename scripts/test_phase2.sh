#!/bin/bash

# Test script for Phase 2: Benefit Verification
# This script tests all the Phase 2 API endpoints

echo "========================================"
echo "Phase 2: Benefit Verification Tests"
echo "========================================"
echo ""

BASE_URL="http://localhost:8000"

# Test 1: Check health endpoint
echo "1. Testing health endpoint..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

# Test 2: Check system info (should show database connected)
echo "2. Testing system info..."
curl -s "$BASE_URL/info" | python3 -m json.tool
echo ""

# Test 3: List all insurance plans
echo "3. Listing all insurance plans..."
curl -s "$BASE_URL/benefit-verification/plans" | python3 -m json.tool
echo ""

# Test 4: List all drugs
echo "4. Listing all drugs..."
curl -s "$BASE_URL/benefit-verification/drugs" | python3 -m json.tool
echo ""

# Test 5: Check patient coverage (P001 + Ozempic)
echo "5. Checking coverage for Patient P001 with Ozempic..."
curl -s -X POST "$BASE_URL/benefit-verification/check-coverage" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "P001", "drug": "Ozempic"}' | python3 -m json.tool
echo ""

# Test 6: Check patient insurance info
echo "6. Getting patient insurance info for P001..."
curl -s "$BASE_URL/benefit-verification/patient/P001/insurance" | python3 -m json.tool
echo ""

# Test 7: Check plan coverage (Aetna Gold + Metformin)
echo "7. Checking plan coverage for Aetna Gold + Metformin..."
curl -s -X POST "$BASE_URL/benefit-verification/check-plan-coverage" \
  -H "Content-Type: application/json" \
  -d '{"plan": "Aetna Gold", "drug": "Metformin"}' | python3 -m json.tool
echo ""

# Test 8: Get alternative drugs for a plan
echo "8. Getting alternative drugs for Aetna Gold..."
curl -s "$BASE_URL/benefit-verification/plan/Aetna%20Gold/alternatives" | python3 -m json.tool
echo ""

echo "========================================"
echo "Phase 2 Tests Complete!"
echo "========================================"

