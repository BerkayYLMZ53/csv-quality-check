"""Profile the shape and completeness of a CSV without modifying it."""

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import sys


def delimiter_value(value):
    value = "\t" if value == r"\t" else value
    if len(value) != 1 or value in '\r\n"\0':
        raise argparse.ArgumentTypeError("Ayraç tek bir karakter olmalı. Sekme için \\t kullan.")
    return value


def profile(path, delimiter=",", encoding="utf-8-sig"):
    with path.open(encoding=encoding, newline="") as source:
        reader = csv.reader(source, delimiter=delimiter, strict=True)
        try:
            headers = next(reader, [])
            if not headers:
                raise ValueError("Başlık satırı bulunamadı.")

            columns = [
                {"position": position, "header": header, "blank_cells": 0}
                for position, header in enumerate(headers, 1)
            ]
            blank_headers = [column["position"] for column in columns if not column["header"].strip()]
            duplicate_headers = [name for name, count in Counter(headers).items() if count > 1]
            valid_rows = 0
            invalid_rows = 0
            invalid_examples = []
            while True:
                first_line = reader.line_num + 1
                row = next(reader, None)
                if row is None:
                    break
                if len(row) != len(headers):
                    invalid_rows += 1
                    if len(invalid_examples) < 10:
                        invalid_examples.append({
                            "start_line": first_line,
                            "end_line": reader.line_num,
                            "fields": len(row),
                        })
                    continue
                valid_rows += 1
                for column, cell in zip(columns, row):
                    if not cell.strip():
                        column["blank_cells"] += 1
        except csv.Error as error:
            raise ValueError(f"CSV sözdizimi hatası (satır {reader.line_num}): {error}") from error

    return {
        "rows": valid_rows + invalid_rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "blank_headers": blank_headers,
        "duplicate_headers": duplicate_headers,
        "columns": columns,
        "invalid_examples": invalid_examples,
    }


def print_report(report):
    print(f"Satır: {report['rows']} | Geçerli: {report['valid_rows']} | Hatalı: {report['invalid_rows']}")
    if report["blank_headers"]:
        print("Boş başlık konumları:", ", ".join(map(str, report["blank_headers"])))
    if report["duplicate_headers"]:
        print("Tekrarlanan başlıklar:", ", ".join(map(repr, report["duplicate_headers"])))
    for column in report["columns"]:
        print(f"{column['position']:>3}. {column['header']!r}: {column['blank_cells']} boş hücre")
    for example in report["invalid_examples"]:
        print(f"Satır {example['start_line']}–{example['end_line']}: {example['fields']} alan bulundu.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="İncelenecek CSV dosyası")
    parser.add_argument("--delimiter", type=delimiter_value, default=",", help=r"Ayraç. Sekme için \t")
    parser.add_argument("--encoding", default="utf-8-sig", help="Dosyanın karakter kodlaması")
    parser.add_argument("--json", action="store_true", help="Raporu JSON olarak yaz")
    parser.add_argument("--fail-on-issues", action="store_true", help="Yapısal sorun varsa çıkış kodu 1 döndür")
    args = parser.parse_args(argv)

    try:
        report = profile(args.input, args.delimiter, args.encoding)
    except (OSError, LookupError, ValueError) as error:
        print(f"Denetim tamamlanamadı: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print_report(report)
    issues = report["invalid_rows"] or report["blank_headers"] or report["duplicate_headers"]
    return 1 if args.fail_on_issues and issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
