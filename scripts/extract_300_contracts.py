#!/usr/bin/env python3
"""
Extract 300 Individual Contract Files from EXECUTOR_CONTRACTS_300_FINAL.json

This script splits the master contract file into individual Q001.v3.json ... Q300.v3.json files
for use by DynamicContractExecutor.

Usage:
    python scripts/extract_300_contracts.py \
      --input artifacts/data/contracts/EXECUTOR_CONTRACTS_300_FINAL.json \
      --output executor_contracts/specialized/
"""

import argparse
import json
import re
import sys
from pathlib import Path


def extract_policy_and_question(contract_id: str) -> tuple[int, int] | None:
    """
    Extract policy area and question number from contract_id.

    Example: 'D01_MUJER_GENERO_Q001_CONTRACT' -> (1, 1)
             'D02_EDUCACION_Q015_CONTRACT' -> (2, 15)
             'D10_VIVIENDA_Q030_CONTRACT' -> (10, 30)

    Returns:
        tuple of (policy_area_number, question_number) or None
    """
    match = re.search(r"D(\d{2})_.*_Q(\d{3})", contract_id)
    if match:
        policy_num = int(match.group(1))
        question_num = int(match.group(2))
        return (policy_num, question_num)
    return None


def compute_global_question_id(policy_num: int, question_num: int) -> int:
    """
    Compute global question ID (Q001-Q300) from policy area and question number.

    Formula: global_id = (policy_num - 1) * 30 + question_num

    Examples:
        D01 Q001 -> Q001 (0*30 + 1)
        D01 Q030 -> Q030 (0*30 + 30)
        D02 Q001 -> Q031 (1*30 + 1)
        D10 Q030 -> Q300 (9*30 + 30)
    """
    return (policy_num - 1) * 30 + question_num


def main():
    parser = argparse.ArgumentParser(
        description="Extract 300 individual contract files from master contract JSON"
    )
    parser.add_argument(
        "--input", type=Path, required=True, help="Path to EXECUTOR_CONTRACTS_300_FINAL.json"
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="Output directory for individual contract files"
    )
    parser.add_argument("--version", type=str, default="v3", help="Contract version (default: v3)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print what would be done without writing files"
    )

    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        print(f"❌ Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Load master contract file
    print(f"📖 Loading master contract file: {args.input}")
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse JSON: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error: Failed to read file: {e}", file=sys.stderr)
        return 1

    # Extract contracts
    contracts = data.get("contracts", {})
    if not contracts:
        print("❌ Error: No contracts found in input file", file=sys.stderr)
        return 1

    print(f"✅ Found {len(contracts)} contracts")

    # Create output directory
    if not args.dry_run:
        args.output.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory: {args.output}")

    # Extract each contract
    extracted_count = 0
    errors = []

    for contract_id, contract_data in contracts.items():
        # Extract policy area and question number
        result = extract_policy_and_question(contract_id)
        if result is None:
            errors.append(f"⚠️  Could not extract policy/question from: {contract_id}")
            continue

        policy_num, question_num = result

        # Compute global question ID (Q001-Q300)
        global_q_id = compute_global_question_id(policy_num, question_num)

        # Generate filename: Q001.v3.json, Q002.v3.json, etc.
        filename = f"Q{global_q_id:03d}.{args.version}.json"
        output_path = args.output / filename

        # Prepare individual contract file structure
        # Include metadata but only this specific contract
        individual_contract = {
            "metadata": {
                "version": data.get("metadata", {}).get("version", "1.0.0"),
                "date": data.get("metadata", {}).get("date", "2025-12-31"),
                "contract_id": contract_id,
                "question_id": f"Q{global_q_id:03d}",
                "original_question_id": f"Q{question_num:03d}",
                "policy_area_number": policy_num,
                "policy_area": contract_data.get("policy_area", ""),
                "protocol": data.get("metadata", {}).get("protocol", "PROMPT_MAESTRO_V1"),
                "compliance": data.get("metadata", {}).get("compliance", []),
                "schema_version": args.version,
            },
            "contract": contract_data,
        }

        if args.dry_run:
            print(f"  Would write: {filename} ({contract_id})")
        else:
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(individual_contract, f, indent=2, ensure_ascii=False)
                extracted_count += 1
                if extracted_count % 30 == 0:
                    print(f"  Progress: {extracted_count}/300 contracts extracted...")
            except Exception as e:
                errors.append(f"❌ Failed to write {filename}: {e}")

    # Summary
    print()
    print("=" * 60)
    if args.dry_run:
        print(f"🔍 DRY RUN: Would extract {len(contracts)} contracts")
    else:
        print(f"✅ Successfully extracted {extracted_count} contracts to {args.output}")

    if errors:
        print(f"\n⚠️  {len(errors)} errors occurred:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

    print("=" * 60)

    return 0 if extracted_count == 300 else 1


if __name__ == "__main__":
    sys.exit(main())
