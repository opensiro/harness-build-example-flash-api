"""Derive a transparent, non-decisional summary from actual native Cognee results.

This never reads assessments or upstream repositories. Scores are literal query
token overlaps for triage, not performance or Cognee's native ranking scores.
"""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path
import re


PROJECT = Path(__file__).resolve().parents[1]
IGNORE = frozenset({"the", "and", "with", "through", "from", "after", "into",
                    "for", "test", "agent", "coding", "python"})


def terms(s):
    return frozenset(w for w in re.findall(r"[a-z]{3,}", s.lower()) if w not in IGNORE)


def main():
    source = PROJECT / "receipts/discovery/native-lexical-results.json"
    obj = json.loads(source.read_text())
    records = []
    for item in obj["results"]:
        qtokens = terms(item["query"])
        if item["status"] != "RETURNED":
            records.append({"query_id":item["query_id"],"status":item["status"],
                            "error":item.get("error"),"hits":[]})
            continue
        hits = []
        for rank, r in enumerate(item["raw_response"][0].get("search_result", []), 1):
            text = r.get("text", "")
            source_id = r.get("document_id", "")
            matched = sorted(qtokens & terms(text))
            hits.append({
                "native_rank":rank, "source_id":source_id,
                "document_name":r.get("document_name"), "function_heading":next(
                    (line.strip() for line in text.splitlines() if line.startswith("## ")),None),
                "query_overlap_terms":matched, "overlap_count":len(matched),
                "chunk_sha256":hashlib.sha256(text.encode()).hexdigest(),
                "chunk_preview":text[:500],
            })
        records.append({"query_id":item["query_id"], "query":item["query"],
                        "status":item["status"],"native_hits":len(hits),
                        "literal_nonzero_overlap":sum(h["overlap_count"]>0 for h in hits),
                        "hits":hits})
    out={"source":"receipts/discovery/native-lexical-results.json",
         "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
         "warning":"Overlap is a simple local triage annotation, not a Cognee score or proof of architectural fit. All raw hits, including irrelevant hits, remain in the source receipt.",
         "queries":records}
    target=PROJECT/"receipts/discovery/hit-index.json"
    target.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    for q in records:
        if "hits" not in q:continue
        print(q["query_id"],"hits",len(q["hits"]),"nonzero",q["literal_nonzero_overlap"])
        for h in q["hits"][:6]:
            print(" ",h["native_rank"],h["source_id"].split(":")[-1],
                  h["function_heading"],"tokens",",".join(h["query_overlap_terms"]))
    print("WROTE",target)


if __name__=="__main__":
    main()
