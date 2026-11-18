from __future__ import annotations

import struct
import sys
from pathlib import Path


KIND_EXTRA = {
    1: 4,   # INT
    2: 0,   # PTR
    3: 12,  # ARRAY
    4: 12,  # STRUCT
    5: 12,  # UNION
    6: 8,   # ENUM
    7: 0,   # FWD
    8: 0,   # TYPEDEF
    9: 0,   # VOLATILE
    10: 0,  # CONST
    11: 0,  # RESTRICT
    12: 0,  # FUNC
    13: 8,  # FUNC_PROTO
    14: 4,  # VAR
    15: 12, # DATASEC
    16: 0,  # FLOAT
    17: 4,  # DECL_TAG
    18: 0,  # TYPE_TAG
    19: 12, # ENUM64
}

KIND_NAMES = {
    1: "INT",
    2: "PTR",
    3: "ARRAY",
    4: "STRUCT",
    5: "UNION",
    6: "ENUM",
    7: "FWD",
    8: "TYPEDEF",
    9: "VOLATILE",
    10: "CONST",
    11: "RESTRICT",
    12: "FUNC",
    13: "FUNC_PROTO",
    14: "VAR",
    15: "DATASEC",
    16: "FLOAT",
    17: "DECL_TAG",
    18: "TYPE_TAG",
    19: "ENUM64",
}


def cstr(strings: bytes, offset: int) -> str:
    if offset <= 0 or offset >= len(strings):
        return ""
    end = strings.find(b"\0", offset)
    if end < 0:
        end = len(strings)
    return strings[offset:end].decode("utf-8", "replace")


def parse_btf(data: bytes, base: int) -> tuple[bytes, list[dict[str, object]]]:
    magic, version, flags, hdr_len, type_off, type_len, str_off, str_len = struct.unpack_from(
        "<HBBIIIII", data, base
    )
    if magic != 0xEB9F:
        raise ValueError("Not a BTF payload")
    total = hdr_len + max(type_off + type_len, str_off + str_len)
    blob = data[base : base + total]
    types_start = base + hdr_len + type_off
    types_end = types_start + type_len
    strings_start = base + hdr_len + str_off
    strings_end = strings_start + str_len
    strings = data[strings_start:strings_end]
    records = []
    offset = types_start
    type_id = 1
    while offset < types_end:
        name_off, info, size_or_type = struct.unpack_from("<III", data, offset)
        vlen = info & 0xFFFF
        kind = (info >> 24) & 0x1F
        kind_flag = bool(info & 0x80000000)
        if kind not in KIND_EXTRA:
            raise ValueError(f"Unknown BTF kind {kind} at offset 0x{offset:x}")
        extra_size = vlen * KIND_EXTRA[kind] if kind in (4, 5, 6, 13, 15, 19) else KIND_EXTRA[kind]
        member_base = offset + 12
        members = []
        params = []
        if kind in (4, 5):
            for index in range(vlen):
                member_name, member_type, member_offset = struct.unpack_from(
                    "<III", data, member_base + index * 12
                )
                bit_offset = member_offset & 0xFFFFFF if kind_flag else member_offset
                bitfield_size = member_offset >> 24 if kind_flag else 0
                members.append(
                    {
                        "name": cstr(strings, member_name),
                        "type_id": member_type,
                        "offset": bit_offset,
                        "bitfield_size": bitfield_size,
                    }
                )
        elif kind == 13:
            for index in range(vlen):
                param_name, param_type = struct.unpack_from(
                    "<II", data, member_base + index * 8
                )
                params.append(
                    {
                        "name": cstr(strings, param_name),
                        "type_id": param_type,
                    }
                )
        record = {
            "id": type_id,
            "name": cstr(strings, name_off),
            "kind": kind,
            "kind_name": KIND_NAMES[kind],
            "vlen": vlen,
            "kind_flag": kind_flag,
            "size_or_type": size_or_type,
            "members": members,
            "params": params,
            "offset": offset,
        }
        records.append(record)
        offset = member_base + extra_size
        type_id += 1
    return blob, records


def main(paths: list[str], output_dir: str) -> None:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    for raw_path in paths:
        path = Path(raw_path)
        data = path.read_bytes()
        base = data.find(b"\x9f\xeb\x01\x00")
        if base < 0:
            raise ValueError(f"BTF magic not found in {path}")
        blob, records = parse_btf(data, base)
        output = destination / f"{path.stem}.btf"
        output.write_bytes(blob)
        print(f"FILE={path.name}")
        print(f"  BTF_OFFSET=0x{base:x} BTF_SIZE={len(blob)} TYPES={len(records)}")
        print(f"  BTF_OUTPUT={output}")
        for record in records:
            name = str(record["name"])
            if (
                "inode_security" in name
                or name in {"list_head", "inode", "super_block", "task_struct"}
                or ("selinux" in name.lower() and record["kind_name"] in {"STRUCT", "UNION", "TYPEDEF"})
            ):
                print(
                    f"  TYPE id={record['id']} kind={record['kind_name']} "
                    f"name={name} size_or_type=0x{record['size_or_type']:x} "
                    f"vlen={record['vlen']} kind_flag={record['kind_flag']}"
                )
                for member in record["members"]:
                    print(
                        f"    +0x{member['offset'] // 8:x} "
                        f"(bit {member['offset']}) "
                        f"type={member['type_id']} "
                        f"name={member['name']} "
                        f"bitfield={member['bitfield_size']}"
                    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("usage: extract_btf_types.py OUTPUT_DIR KERNEL_IMAGE [...]")
    main(sys.argv[2:], sys.argv[1])
