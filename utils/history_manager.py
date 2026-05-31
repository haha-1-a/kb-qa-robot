import csv
import json
import os
from datetime import datetime
from typing import List, Optional


class HistoryManager:
    def __init__(self, history_path: str = None):
        self.history_path = history_path or "./data/history.json"
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.history_path):
            self._write_records([])

    def _read_records(self) -> list:
        with open(self.history_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_records(self, records: list):
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def add_record(self, question: str, answer: str, sources: list):
        records = self._read_records()
        records.insert(0, {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "answer": answer,
            "sources": [
                {"source": s[1].get("source", ""), "score": round(s[2], 4), "text": s[0][:200]}
                for s in sources
            ],
        })
        self._write_records(records)

    def get_records(self, limit: int = 50) -> list:
        records = self._read_records()
        return records[:limit]

    def export_to_csv(self, output_path: str):
        records = self._read_records()
        with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["时间", "问题", "回答", "引用来源"])
            for r in records:
                sources_text = "; ".join(
                    f"{s['source']}({s['score']:.2f})" for s in r.get("sources", [])
                )
                writer.writerow([r["timestamp"], r["question"], r["answer"], sources_text])

    def get_record_by_index(self, index: int) -> Optional[dict]:
        records = self._read_records()
        if 0 <= index < len(records):
            return records[index]
        return None

    def clear(self):
        self._write_records([])
