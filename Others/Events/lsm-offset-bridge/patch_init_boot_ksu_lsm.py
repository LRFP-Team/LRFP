from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import lzma
import os
import struct
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs
from capstone.arm64 import (
    ARM64_INS_ADD,
    ARM64_INS_ADRP,
    ARM64_INS_LDR,
    ARM64_INS_LDRSW,
    ARM64_INS_STR,
    ARM64_OP_MEM,
    ARM64_OP_REG,
)
from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
from lz4 import block as lz4_block
from lz4 import frame as lz4_frame

from extract_btf_types import parse_btf


ANDROID_MAGIC = b"ANDROID!"
CPIO_MAGICS = (b"070701", b"070702")
LEGACY_LZ4_MAGIC = b"\x02\x21\x4c\x18"
LZ4_FRAME_MAGIC = b"\x04\x22\x4d\x18"
XZ_MAGIC = b"\xfd\x37\x7a\x58\x5a\x00"
GZIP_MAGIC = b"\x1f\x8b"
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"
MAX_LEGACY_LZ4_BLOCK = 8 * 1024 * 1024
SHF_EXECINSTR = 0x4
R_AARCH64_ADR_PREL_PG_HI21 = 275
R_AARCH64_LDST32_ABS_LO12_NC = 285


class PatchError(RuntimeError):
    pass


@dataclass(frozen=True)
class BootImage:
    header_version: int
    kernel_size: int
    ramdisk_size: int
    ramdisk_offset: int
    payload_end: int
    avb_footer: dict[str, int] | None


@dataclass(frozen=True)
class CpioEntry:
    header_start: int
    payload_start: int
    payload_end: int
    payload: bytes


@dataclass(frozen=True)
class Relocation:
    section_name: str
    section_offset: int
    entry_index: int
    entry_size: int
    site: int
    relocation_type: int
    symbol_name: str
    addend: int
    target_section: str

    @property
    def addend_file_offset(self) -> int:
        return self.section_offset + self.entry_index * self.entry_size + 16


@dataclass(frozen=True)
class SidRelocationTarget:
    store_site: int
    store_text: str
    add_relocation: Relocation
    load_relocation: Relocation

    @property
    def current_addend(self) -> int:
        if self.add_relocation.addend != self.load_relocation.addend:
            raise PatchError(
                "Relocation pair has different addends: "
                f"{self.add_relocation.addend} and {self.load_relocation.addend}"
            )
        return self.add_relocation.addend

    @property
    def sites(self) -> tuple[int, int]:
        return (self.add_relocation.site, self.load_relocation.site)


def align(value: int, boundary: int) -> int:
    return (value + boundary - 1) & -boundary


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cstr(strings: bytes, offset: int) -> str:
    if offset <= 0 or offset >= len(strings):
        return ""
    end = strings.find(b"\0", offset)
    if end < 0:
        end = len(strings)
    return strings[offset:end].decode("utf-8", "replace")


def load_btf_records(path: Path) -> list[dict[str, object]]:
    data = path.read_bytes()
    base = data.find(b"\x9f\xeb\x01\x00")
    if base < 0:
        raise PatchError(f"BTF magic not found in {path}")
    _, records = parse_btf(data, base)
    if not records:
        raise PatchError(f"No BTF records parsed from {path}")
    return records


def find_struct(
    records: list[dict[str, object]], name: str
) -> dict[str, object]:
    matches = [
        record
        for record in records
        if record["kind_name"] == "STRUCT" and record["name"] == name
    ]
    if not matches:
        raise PatchError(f"BTF struct {name!r} not found")
    signatures = {
        tuple(
            (str(member["name"]), int(member["offset"]))
            for member in record["members"]
        )
        for record in matches
    }
    if len(signatures) != 1:
        raise PatchError(f"Ambiguous BTF definitions for struct {name!r}")
    return matches[0]


def member_offset(record: dict[str, object], name: str) -> int:
    matches = [
        int(member["offset"]) // 8
        for member in record["members"]
        if member["name"] == name
    ]
    if len(matches) != 1:
        raise PatchError(
            f"Expected one member {record['name']}.{name}, found {len(matches)}"
        )
    return matches[0]


def lsm_layout(btf_path: Path) -> tuple[int, int, dict[int, str]]:
    records = load_btf_records(btf_path)
    lsm = find_struct(records, "lsm_blob_sizes")
    inode_security = find_struct(records, "inode_security_struct")
    inode_offset = member_offset(lsm, "lbs_inode")
    sid_offset = member_offset(inode_security, "sid")
    field_names = {
        int(member["offset"]) // 8: str(member["name"])
        for member in lsm["members"]
    }
    return inode_offset, sid_offset, field_names


def detect_compression(data: bytes) -> str:
    if data.startswith(LEGACY_LZ4_MAGIC):
        return "legacy-lz4"
    if data.startswith(LZ4_FRAME_MAGIC):
        return "lz4-frame"
    if data.startswith(GZIP_MAGIC):
        return "gzip"
    if data.startswith(XZ_MAGIC):
        return "xz"
    if data.startswith(ZSTD_MAGIC):
        return "zstd"
    if data[:1] == b"\x5d" and len(data) >= 13:
        return "lzma-alone"
    raise PatchError(f"Unsupported ramdisk compression: {data[:8].hex()}")


def decompress_legacy_lz4(data: bytes) -> bytes:
    offset = len(LEGACY_LZ4_MAGIC)
    output = bytearray()
    while offset + 4 <= len(data):
        block_size = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        block = data[offset : offset + block_size]
        if len(block) != block_size:
            raise PatchError("Truncated legacy LZ4 block")
        offset += block_size
        decompressed = lz4_block.decompress(
            block, uncompressed_size=MAX_LEGACY_LZ4_BLOCK
        )
        output.extend(decompressed)
        if len(decompressed) < MAX_LEGACY_LZ4_BLOCK:
            break
    if offset != len(data):
        raise PatchError("Unexpected trailing data in legacy LZ4 stream")
    return bytes(output)


def compress_legacy_lz4(data: bytes) -> bytes:
    output = bytearray(LEGACY_LZ4_MAGIC)
    for offset in range(0, len(data), MAX_LEGACY_LZ4_BLOCK):
        chunk = data[offset : offset + MAX_LEGACY_LZ4_BLOCK]
        block = lz4_block.compress(
            chunk,
            mode="high_compression",
            compression=12,
            store_size=False,
        )
        output.extend(struct.pack("<I", len(block)))
        output.extend(block)
    if decompress_legacy_lz4(bytes(output)) != data:
        raise PatchError("Legacy LZ4 round-trip failed")
    return bytes(output)


def decompress_ramdisk(data: bytes, compression: str) -> bytes:
    if compression == "legacy-lz4":
        return decompress_legacy_lz4(data)
    if compression == "lz4-frame":
        return lz4_frame.decompress(data)
    if compression == "gzip":
        return gzip.decompress(data)
    if compression == "xz":
        return lzma.decompress(data, format=lzma.FORMAT_XZ)
    if compression == "lzma-alone":
        return lzma.decompress(data, format=lzma.FORMAT_ALONE)
    if compression == "zstd":
        try:
            import zstandard
        except ImportError as exc:
            raise PatchError(
                "Zstandard ramdisk requires the Python package 'zstandard'"
            ) from exc
        return zstandard.ZstdDecompressor().decompress(data)
    raise PatchError(f"Unsupported compression: {compression}")


def compress_ramdisk(data: bytes, compression: str) -> bytes:
    if compression == "legacy-lz4":
        result = compress_legacy_lz4(data)
    elif compression == "lz4-frame":
        result = lz4_frame.compress(data, compression_level=12)
    elif compression == "gzip":
        result = gzip.compress(data, compresslevel=9, mtime=0)
    elif compression == "xz":
        result = lzma.compress(data, format=lzma.FORMAT_XZ, preset=9)
    elif compression == "lzma-alone":
        result = lzma.compress(data, format=lzma.FORMAT_ALONE, preset=9)
    elif compression == "zstd":
        try:
            import zstandard
        except ImportError as exc:
            raise PatchError(
                "Zstandard ramdisk requires the Python package 'zstandard'"
            ) from exc
        result = zstandard.ZstdCompressor(level=19).compress(data)
    else:
        raise PatchError(f"Unsupported compression: {compression}")
    if decompress_ramdisk(result, compression) != data:
        raise PatchError(f"{compression} round-trip failed")
    return result


def find_cpio_entry(data: bytes, target_name: str) -> CpioEntry:
    offset = 0
    while offset + 110 <= len(data):
        if data[offset : offset + 6] not in CPIO_MAGICS:
            next_offset = min(
                (
                    found
                    for magic in CPIO_MAGICS
                    if (found := data.find(magic, offset + 1)) >= 0
                ),
                default=-1,
            )
            if next_offset < 0:
                break
            offset = next_offset
            continue

        header = data[offset : offset + 110]
        try:
            fields = [
                int(header[6 + index * 8 : 14 + index * 8], 16)
                for index in range(13)
            ]
        except ValueError:
            offset += 1
            continue
        name_size = fields[11]
        file_size = fields[6]
        name_start = offset + 110
        name_end = name_start + name_size
        if name_size <= 0 or name_end > len(data):
            raise PatchError("Malformed CPIO filename length")
        name = data[name_start : name_end - 1].decode("utf-8", "replace")
        payload_start = align(name_end, 4)
        payload_end = payload_start + file_size
        if payload_end > len(data):
            raise PatchError(f"CPIO entry {name!r} exceeds ramdisk")
        if name == target_name:
            return CpioEntry(
                header_start=offset,
                payload_start=payload_start,
                payload_end=payload_end,
                payload=data[payload_start:payload_end],
            )
        offset = align(payload_end, 4)
        if name == "TRAILER!!!":
            break
    raise PatchError(f"CPIO entry {target_name!r} not found")


def parse_avb_footer(image: bytes) -> dict[str, int] | None:
    footer_offset = image.rfind(b"AVBf")
    if footer_offset < 0:
        return None
    values = struct.unpack_from(">4sIIQQQ28s", image, footer_offset)
    footer = {
        "footer_offset": footer_offset,
        "version": int(values[1]),
        "original_image_size": int(values[3]),
        "vbmeta_offset": int(values[4]),
        "vbmeta_size": int(values[5]),
    }
    if not (
        0 < footer["original_image_size"] <= footer["vbmeta_offset"] <= len(image)
    ):
        raise PatchError("AVB footer has an invalid vbmeta offset")
    return footer


def parse_boot_image(image: bytes) -> BootImage:
    if image[:8] != ANDROID_MAGIC:
        raise PatchError("Input is not an Android boot image")
    if len(image) < 4096:
        raise PatchError("Input image is shorter than one boot-image page")
    header_version = struct.unpack_from("<I", image, 40)[0]
    if header_version not in (3, 4):
        raise PatchError(
            f"Unsupported boot header v{header_version}; expected init_boot v3/v4"
        )
    header_size = struct.unpack_from("<I", image, 20)[0]
    if not 0 < header_size <= 4096:
        raise PatchError(f"Invalid boot header size: {header_size}")
    kernel_size, ramdisk_size = struct.unpack_from("<II", image, 8)
    if kernel_size != 0:
        raise PatchError(
            "This tool expects an init_boot image with kernel_size=0"
        )
    ramdisk_offset = 4096
    if ramdisk_offset + ramdisk_size > len(image):
        raise PatchError("Ramdisk extends beyond the input image")
    footer = parse_avb_footer(image)
    payload_end = footer["vbmeta_offset"] if footer else len(image)
    if payload_end < ramdisk_offset + ramdisk_size:
        raise PatchError("Ramdisk overlaps the AVB vbmeta area")
    return BootImage(
        header_version=header_version,
        kernel_size=kernel_size,
        ramdisk_size=ramdisk_size,
        ramdisk_offset=ramdisk_offset,
        payload_end=payload_end,
        avb_footer=footer,
    )


def collect_relocations(module: bytes) -> tuple[list[Relocation], set[str]]:
    relocations: list[Relocation] = []
    executable_sections: set[str] = set()
    with io.BytesIO(module) as stream:
        elf = ELFFile(stream)
        for target_section in elf.iter_sections():
            flags = int(target_section["sh_flags"])
            if flags & SHF_EXECINSTR and int(target_section["sh_size"]) > 0:
                executable_sections.add(target_section.name)

        for section in elf.iter_sections():
            if not isinstance(section, RelocationSection):
                continue
            target_index = int(section["sh_info"])
            if target_index <= 0:
                continue
            target_section = elf.get_section(target_index)
            if target_section.name not in executable_sections:
                continue
            symbols = elf.get_section(section["sh_link"])
            entry_size = int(section["sh_entsize"])
            if entry_size < 24:
                raise PatchError(
                    f"Unexpected relocation entry size in {section.name}"
                )
            for index, relocation in enumerate(section.iter_relocations()):
                symbol = symbols.get_symbol(int(relocation["r_info_sym"]))
                relocations.append(
                    Relocation(
                        section_name=section.name,
                        section_offset=int(section["sh_offset"]),
                        entry_index=index,
                        entry_size=entry_size,
                        site=int(relocation["r_offset"]),
                        relocation_type=int(relocation["r_info_type"]),
                        symbol_name=symbol.name,
                        addend=int(relocation["r_addend"]),
                        target_section=target_section.name,
                    )
                )
    if not executable_sections:
        raise PatchError("No executable sections found in KernelSU module")
    return relocations, executable_sections


def register_name(instruction, operand_index: int) -> str:
    operand = instruction.operands[operand_index]
    if operand.type != ARM64_OP_REG:
        return ""
    return instruction.reg_name(operand.reg).lower()


def find_sid_relocation_targets(
    module: bytes, sid_offset: int
) -> tuple[list[SidRelocationTarget], list[Relocation]]:
    relocations, executable_sections = collect_relocations(module)
    blob_relocations = [
        relocation
        for relocation in relocations
        if relocation.symbol_name == "selinux_blob_sizes"
    ]
    if not blob_relocations:
        raise PatchError(
            "No relocations to selinux_blob_sizes were found in executable code"
        )

    targets: dict[tuple[int, int], SidRelocationTarget] = {}
    disassembler = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    disassembler.detail = True
    disassembler.skipdata = True

    with io.BytesIO(module) as stream:
        elf = ELFFile(stream)
        for section_name in sorted(executable_sections):
            section = elf.get_section_by_name(section_name)
            if section is None:
                continue
            section_relocations = [
                relocation
                for relocation in blob_relocations
                if relocation.target_section == section_name
            ]
            if not section_relocations:
                continue
            instructions = list(
                disassembler.disasm(section.data(), int(section["sh_addr"]))
            )
            by_address = {instruction.address: instruction for instruction in instructions}
            ordered = sorted(instructions, key=lambda instruction: instruction.address)

            for store in ordered:
                if store.id != ARM64_INS_STR:
                    continue
                if len(store.operands) != 2:
                    continue
                if (
                    store.operands[0].type != ARM64_OP_REG
                    or store.operands[1].type != ARM64_OP_MEM
                ):
                    continue
                memory = store.operands[1].mem
                if memory.disp != sid_offset:
                    continue
                store_base = store.reg_name(memory.base).lower()
                if not store_base.startswith("x"):
                    continue

                for add_relocation in section_relocations:
                    if add_relocation.relocation_type != R_AARCH64_ADR_PREL_PG_HI21:
                        continue
                    for load_relocation in section_relocations:
                        if (
                            load_relocation.relocation_type
                            != R_AARCH64_LDST32_ABS_LO12_NC
                        ):
                            continue
                        if load_relocation.site <= add_relocation.site:
                            continue
                        if load_relocation.site - add_relocation.site > 8:
                            continue
                        if load_relocation.site >= store.address:
                            continue
                        if store.address - load_relocation.site > 0x50:
                            continue
                        add_insn = by_address.get(add_relocation.site)
                        load_insn = by_address.get(load_relocation.site)
                        if add_insn is None or load_insn is None:
                            continue
                        if add_insn.id != ARM64_INS_ADRP:
                            continue
                        if load_insn.id not in (ARM64_INS_LDR, ARM64_INS_LDRSW):
                            continue
                        adrp_destination = register_name(add_insn, 0)
                        loaded_destination = register_name(load_insn, 0)
                        if (
                            not adrp_destination.startswith("x")
                            or adrp_destination != loaded_destination
                        ):
                            continue

                        pair_end = load_relocation.site
                        add_matches = False
                        for instruction in ordered:
                            if instruction.address <= pair_end:
                                continue
                            if instruction.address >= store.address:
                                break
                            if instruction.id != ARM64_INS_ADD:
                                continue
                            if len(instruction.operands) != 3:
                                continue
                            if register_name(instruction, 0) != store_base:
                                continue
                            sources = {
                                register_name(instruction, 1),
                                register_name(instruction, 2),
                            }
                            if (
                                adrp_destination in sources
                                and any(source.startswith("x") for source in sources)
                            ):
                                add_matches = True
                                break
                        if not add_matches:
                            continue

                        target = SidRelocationTarget(
                            store_site=store.address,
                            store_text=(
                                f"{store.mnemonic} {store.op_str}"
                            ),
                            add_relocation=add_relocation,
                            load_relocation=load_relocation,
                        )
                        targets[target.sites] = target

    if not targets:
        raise PatchError(
            "Could not find a selinux_blob_sizes relocation pair feeding "
            f"a write to inode_security_struct.sid (+0x{sid_offset:x}). "
            "The module may use a different inlined implementation or ABI."
        )
    return sorted(targets.values(), key=lambda target: target.store_site), blob_relocations


def patch_module(module: bytes, inode_offset: int, sid_offset: int) -> tuple[bytes, list[SidRelocationTarget]]:
    targets, _ = find_sid_relocation_targets(module, sid_offset)
    patched = bytearray(module)
    for target in targets:
        for relocation in (target.add_relocation, target.load_relocation):
            if relocation.addend == inode_offset:
                continue
            struct.pack_into(
                "<q", patched, relocation.addend_file_offset, inode_offset
            )

    verified_targets, _ = find_sid_relocation_targets(bytes(patched), sid_offset)
    verified_sites = {target.sites for target in verified_targets}
    if verified_sites != {target.sites for target in targets}:
        raise PatchError("Patched relocation sites no longer match after verification")
    if any(target.current_addend != inode_offset for target in verified_targets):
        raise PatchError("Patched relocations do not all use the requested addend")
    return bytes(patched), targets


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def replace_ramdisk_module(
    image: bytes,
    boot: BootImage,
    module_name: str,
    patched_module: bytes,
) -> tuple[bytes, str, bytes]:
    compressed = image[
        boot.ramdisk_offset : boot.ramdisk_offset + boot.ramdisk_size
    ]
    compression = detect_compression(compressed)
    ramdisk = decompress_ramdisk(compressed, compression)
    entry = find_cpio_entry(ramdisk, module_name)
    if len(entry.payload) != len(patched_module):
        raise PatchError(
            "Patched module size changed; this tool intentionally refuses to "
            "rebuild CPIO metadata"
        )
    if entry.payload == patched_module:
        return image, compression, ramdisk
    patched_ramdisk = bytearray(ramdisk)
    patched_ramdisk[entry.payload_start : entry.payload_end] = patched_module
    new_compressed = compress_ramdisk(bytes(patched_ramdisk), compression)
    old_end = boot.ramdisk_offset + boot.ramdisk_size
    new_end = boot.ramdisk_offset + len(new_compressed)
    if new_end > boot.payload_end:
        raise PatchError(
            "Recompressed ramdisk does not fit before the AVB vbmeta area"
        )
    if new_end > old_end:
        gap = image[old_end:new_end]
        if any(gap):
            raise PatchError(
                "Recompressed ramdisk would overwrite non-padding image data"
            )

    output = bytearray(image)
    struct.pack_into("<I", output, 12, len(new_compressed))
    output[boot.ramdisk_offset : max(old_end, new_end)] = b"\0" * (
        max(old_end, new_end) - boot.ramdisk_offset
    )
    output[boot.ramdisk_offset:new_end] = new_compressed
    if boot.payload_end < len(output) and output[boot.payload_end :] != image[
        boot.payload_end :
    ]:
        raise PatchError("AVB footer or partition tail changed unexpectedly")

    verify_image = bytes(output)
    verify_size = struct.unpack_from("<I", verify_image, 12)[0]
    verify_ramdisk = decompress_ramdisk(
        verify_image[boot.ramdisk_offset : boot.ramdisk_offset + verify_size],
        compression,
    )
    verify_entry = find_cpio_entry(verify_ramdisk, module_name)
    if verify_entry.payload != patched_module:
        raise PatchError("Verification failed: patched module was not persisted")
    return verify_image, compression, verify_ramdisk


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Patch the inode SID write in a KernelSU-family module inside an "
            "Android init_boot image. The target LSM field is read from kernel BTF; "
            "the relocation sites are located from the module's AArch64 code."
        )
    )
    parser.add_argument("input_image", type=Path)
    parser.add_argument(
        "--btf",
        required=True,
        type=Path,
        help="Kernel BTF blob or kernel Image containing an embedded .BTF section",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--module-name",
        default="kernelsu.ko",
        help="CPIO module path to patch (default: kernelsu.ko)",
    )
    parser.add_argument(
        "--ko-output",
        type=Path,
        help="Optionally write the patched module ELF separately",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze and verify in memory without writing the output image",
    )
    args = parser.parse_args()

    if args.input_image.resolve() == args.output.resolve():
        raise PatchError("Refusing to overwrite the input image")

    image = args.input_image.read_bytes()
    boot = parse_boot_image(image)
    compressed = image[
        boot.ramdisk_offset : boot.ramdisk_offset + boot.ramdisk_size
    ]
    compression = detect_compression(compressed)
    ramdisk = decompress_ramdisk(compressed, compression)
    entry = find_cpio_entry(ramdisk, args.module_name)
    original_module = entry.payload

    inode_offset, sid_offset, lsm_fields = lsm_layout(args.btf)
    _, all_relocations = find_sid_relocation_targets(original_module, sid_offset)
    patched_module, targets = patch_module(
        original_module, inode_offset, sid_offset
    )
    changed_module_offsets = [
        index
        for index, (before, after) in enumerate(
            zip(original_module, patched_module)
        )
        if before != after
    ]
    output_image, compression, _ = replace_ramdisk_module(
        image, boot, args.module_name, patched_module
    )

    print(f"input_image={args.input_image.resolve()}")
    print(f"input_image_sha256={sha256(image)}")
    print(f"btf={args.btf.resolve()}")
    print(f"btf_lbs_inode_offset=0x{inode_offset:x}")
    print(f"btf_inode_security_sid_offset=0x{sid_offset:x}")
    old_fields = sorted(
        {
            f"+0x{target.current_addend:x}"
            f"({lsm_fields.get(target.current_addend, 'unknown')})"
            for target in targets
        }
    )
    print(f"old_relocation_offsets={','.join(old_fields)}")
    print(f"module_entry={args.module_name}")
    print(f"module_sha256_before={sha256(original_module)}")
    print(f"module_sha256_after={sha256(patched_module)}")
    print(f"compression={compression}")
    print(
        "cpio_payload_offsets="
        f"0x{entry.payload_start:x}..0x{entry.payload_end:x}"
    )
    for target in targets:
        print(
            f"sid_store=0x{target.store_site:x} `{target.store_text}` "
            f"relocations=0x{target.add_relocation.site:x},"
            f"0x{target.load_relocation.site:x} "
            f"{target.current_addend}->{inode_offset}"
        )
    print(f"changed_module_bytes={len(changed_module_offsets)}")
    if changed_module_offsets:
        print(
            "changed_module_offsets="
            + ",".join(f"0x{offset:x}" for offset in changed_module_offsets)
        )
    print(f"selinux_blob_sizes_exec_relocations={len(all_relocations)}")
    print(f"output_image_sha256={sha256(output_image)}")
    if boot.avb_footer:
        print(
            "avb=footer_and_partition_tail_preserved; vbmeta was not re-signed; "
            "bootloader verification must already be disabled"
        )
    else:
        print("avb=no AVB footer detected")

    if args.ko_output:
        atomic_write(args.ko_output, patched_module)
        print(f"ko_output={args.ko_output.resolve()}")
    if args.dry_run:
        print("dry_run=true; no image was written")
    else:
        atomic_write(args.output, output_image)
        print(f"output_image={args.output.resolve()}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PatchError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
