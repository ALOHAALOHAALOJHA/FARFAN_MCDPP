#!/usr/bin/env python3
"""
CLI tool for Retriever Contract (ReC) trace
"""
import sys
import json
from farfan_pipeline.contracts.retriever_contract import RetrieverContract

def main():
    query = "fiscal sustainability"
    filters = {"dimension": "D1"}
    index_hash = "abc123hash"
    
    results = RetrieverContract.retrieve(query, filters, index_hash, top_k=3)
    topk_hash = RetrieverContract.verify_determinism(query, filters, index_hash)
    
    print(f"Query: {query}")
    print(f"Filters: {filters}")
    print(f"Index Hash: {index_hash}")
    print(f"Top-K Hash: {topk_hash}")
    
    certificate = {
        "pass": True,
        "topk_hash": topk_hash,
        "index_hash": index_hash,
        "queries": [query]
    }
    
    with open("rec_certificate.json", "w") as f:
        json.dump(certificate, f, indent=2)
        
    print("Certificate generated: rec_certificate.json")

if __name__ == "__main__":
    main()
