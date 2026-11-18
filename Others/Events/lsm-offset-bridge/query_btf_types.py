from __future__ import annotations

import argparse
import re
from pathlib import Path

from extract_btf_types import parse_btf


def load_types(path: Path):
    data = path.read_bytes()
    base = data.find(b"\x9f\xeb\x01\x00")
    if base < 0:
        raise ValueError(f"BTF magic not found in {path}")
    _, records = parse_btf(data, base)
    return records


def type_label(records, type_id: int) -> str:
    if type_id <= 0 or type_id > len(records):
        return "void"
    record = records[type_id - 1]
    name = str(record["name"])
    kind = str(record["kind_name"])
    if kind == "PTR":
        return f"{type_label(records, int(record['size_or_type']))} *"
    return name or f"<{kind}:{type_id}>"


def render(records, pattern: re.Pattern[str]) -> list[str]:
    output: list[str] = []
    for record in records:
        name = str(record["name"])
        if not pattern.search(name):
            continue
        output.append(
            f"TYPE id={record['id']} kind={record['kind_name']} name={name} "
            f"size_or_type=0x{int(record['size_or_type']):x} "
            f"vlen={record['vlen']} kind_flag={record['kind_flag']}"
        )
        if record["kind_name"] == "FUNC":
            proto_id = int(record["size_or_type"])
            if 0 < proto_id <= len(records):
                proto = records[proto_id - 1]
                ret_type = int(proto["size_or_type"])
                output.append(
                    f"  prototype={proto_id} "
                    f"return={ret_type} ({type_label(records, ret_type)})"
                )
                for index, param in enumerate(proto["params"]):
                    param_type = int(param["type_id"])
                    output.append(
                        f"  param[{index}] type={param_type} "
                        f"({type_label(records, param_type)}) name={param['name']}"
                    )
        for member in record["members"]:
            member_name = str(member["name"])
            member_type = int(member["type_id"])
            bit_offset = int(member["offset"])
            output.append(
                f"  +0x{bit_offset // 8:x} bit={bit_offset} "
                f"type={member_type} "
                f"({type_label(records, member_type)}) "
                f"name={member_name} bitfield={member['bitfield_size']}"
            )
        for index, param in enumerate(record["params"]):
            param_type = int(param["type_id"])
            output.append(
                f"  param[{index}] type={param_type} "
                f"({type_label(records, param_type)}) name={param['name']}"
            )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Query types from a BTF blob.")
    parser.add_argument("btf", type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    records = load_types(args.btf)
    lines = render(records, re.compile(args.name))
    text = "\n".join(lines) + ("\n" if lines else "")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"WROTE={args.output} LINES={len(lines)}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
