# Incident logs

Logs collected from the BakaSU LSM offset incident reported on 2026-10-31.

## before-sanitization

These files are the unmodified source evidence:

- `dmesg.log`: BakaSU dmesg log copied from `/data/adb/ksu/log/dmesg.log`
- `console-ramoops-0`: captured kernel panic console log
- `modules_info`: module inventory captured with the original logs

The raw files contain sensitive device identifiers and must not be committed or published.

## after-sanitization

These files were prepared for the upstream issue report:

- `bakasu-dmesg-sanitized.log`: full sanitized BakaSU dmesg log
- `kernel-panic-sanitized-excerpt.log`: symbolic kernel panic excerpt
- `SANITIZATION.txt`: source hashes, output hashes, and redaction rules
