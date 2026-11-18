### LSM Offset Bridge

This directory stores some Python scripts that temporarily mitigate kernel panics caused when a kernel-level rooting solution accidentally writes into adjacent inode list metadata due to the use of offsets from an older Linux Security Module (LSM) layout on a new layout. 

| Python script | Purpose |
| - | - |
| ``patch_init_boot_ksu_lsm.py`` | BTF-driven KernelSU LSM relocation patcher and init_boot repacker |
| ``extract_btf_types.py`` | Minimal BTF parser used by the patcher |
| ``query_btf_types.py`` | Read-only BTF structure and member inspector |
| ``requirements.txt`` | Python runtime dependencies |

**BakaSU and some other KSU variants have permanently fixed this issue as of October 31, 2026. For details, see [https://github.com/Baka-SU/BakaSU/commit/f98b7a5b909910e1830cae8a2f9c78a61f1f6c2a](https://github.com/Baka-SU/BakaSU/commit/f98b7a5b909910e1830cae8a2f9c78a61f1f6c2a).**

#### Phenomenon

The device suddenly freezes during use. Screen clicks become unresponsive both inside and outside applications, and physical button operations are also ineffective. After approximately a few seconds (usually no more than five seconds), the screen goes black. After another few seconds (usually no more than ten seconds), the device begins to boot. 

After the user enters the power-on password and accesses the desktop, it is found that all the changes made in the tens of seconds before the freeze, while not showing any error messages, were not saved, including but not limited to file saving and Wi-Fi status changes. 

This phenomenon occurs randomly, but mostly after file read/write operations. For example, it is very likely to occur when performing a backup and restore using Swift Backup or when exporting large error logs to the computer via ADB. 

#### The failure

Based on the above phenomena, it is initially speculated that the cache generated in the tens of seconds before the entire system crashed failed to persist to physical storage. Meanwhile, crash logs from various sources were retrieved for investigation, and the initial diagnosis is a kernel panic. 

The incident was reproduced on a OnePlus PJZ110 running Linux ``6.6.144-4k-g9bf326ec3b1e``. A stable kernel update added the ``backing_file`` LSM hook and inserted a new field into ``struct lsm_blob_sizes``: 

```text
Old layout                         New layout

lbs_cred        +0x0               lbs_cred        +0x0
lbs_file        +0x4               lbs_file        +0x4
lbs_inode       +0x8               lbs_backing_file +0x8
lbs_superblock  +0xc               lbs_inode       +0xc
```

The installed ``kernelsu.ko`` was built against the old layout. Its file-wrapper path still read ``selinux_blob_sizes + 0x8``, expecting the inode blob size. On the new kernel, that address contains the backing-file blob size. 

The LSM allocator aligns the inode blob to eight bytes. The stale calculation therefore placed the target eight bytes before the real ``inode_security_struct``. A 32-bit write of ``ksu_file_sid`` landed at: 

```text
inode_security_struct + 0x14
= upper 32 bits of list.prev
```

The corruption did not immediately panic. Later, while cleaning up any affected inode, ``selinux_inode_free_security()`` called ``list_del()`` and detected the malformed list pointer. 
The kernel raised a BUG, resulting in a reboot caused by the kernel panic. That explains both the delayed failures and random occurrence. 
It also explained the repeated ``0x0000005b`` value in the corrupted pointer, where ``0x5b`` was the cached KernelSU file SID. 

The captured kernel panic call stack was: 

```text
list_del corruption: malformed prev/next pointer
__list_del_entry_valid_or_report
selinux_inode_free_security
security_inode_free
__destroy_inode
evict
iput
dentry_unlink_inode
__dentry_kill
dentry_kill
dput
__fput
__fput_sync
__arm64_sys_close
kernel BUG at lib/list_debug.c
Internal error: Oops - BUG: Fatal exception
Kernel panic - not syncing: Oops - BUG: Fatal exception
```

The close/``__fput_sync`` path is the observer in this trace. It detects the damage while releasing an inode; the wrong ``ksu_file_sid`` write described above is the earlier corruption source. 

The relevant instructions in the affected module were: 

```text
0x8698  adrp/ldrsw selinux_blob_sizes + 0x8
0x86ac  ldr       w10, [ksu_file_sid]
0x86b0  str       w10, [x9, #0x1c]
```

The store targets the correct ``sid`` field offset, but the base pointer was calculated from the wrong LSM sub-blob. 

#### Bridge

This problem can be addressed from two perspectives. 

- Kernel developers could remove the `lbs_backing_file` field from the existing kernel to roll back the LSM layout. However, ROM compilation and release cycles are typically long, and most kernels are heavily dependent on upstream components (e.g., the PixelOS kernel depends on the LineageOS kernel, and the LineageOS kernel depends on the Linux kernel). In principle, the LSM layout cannot be reversed. Therefore, this approach is unlikely to be a long-term fundamental solution. 
- A kernel-level root solution could be developed to adapt to the new LSM layout and build a more general LSM location mechanism. 

Theoretically, within the same major version (e.g., 6.6), the kernel architecture (including the LSM layout) should remain relatively stable to reduce the adaptation costs for developers using a generic kernel between minor versions (e.g., 6.6.127 and 6.6.144). However, in practice, kernel versions do not guarantee that the LSM layout will remain unchanged within the same major version. 

This repository serves as a transitional bridge between these two approaches, providing limited transitional fixes. 

#### Repair strategy

The long-term solution remains as described above. However, if the corresponding build is temporarily unavailable, the Python scripts provided in this repository can utilize the relocation information pre-embedded in ``init_boot``, which has been patched by a kernel-level root solution. 

The patcher: 

1. reads the target kernel BTF or an Android kernel ``Image`` containing BTF;
2. resolves ``lsm_blob_sizes.lbs_inode`` and ``inode_security_struct.sid``;
3. extracts the KernelSU module from the init_boot ramdisk;
4. disassembles executable AArch64 sections and finds the store that writes ``sid``;
5. finds the ``ADRP`` plus low-12-bit relocation pair for ``selinux_blob_sizes`` that feeds that store;
6. changes only those relocation addends;
7. recompresses the ramdisk, preserves the AVB footer and partition tail, then verifies the embedded module. 

For the reproduced kernel, the result was: 

```text
lsm_blob_sizes.lbs_inode       +0x8 -> +0x0c
inode_security_struct.sid      +0x1c
modified module relocations    0x8698 and 0x869c
modified module bytes          2
```

The generated image SHA-256 was: 

```text
490b51443ffb4a5d055b0c128e0ca57c93c17ab9ca32e4af264434abb7271142
```

That image was flashed to slot ``_a`` and matched the previously validated repair byte for byte. A later run against the 0912 kernel BTF correctly selected ``lbs_inode=+0x8`` and made no change. 

#### Quick start

Requirements: Python 3.10 or newer, ``capstone``, ``pyelftools``, and ``lz4``. Install optional ``zstandard`` support only when the target ramdisk uses Zstandard. 

```bash
python3 -m pip install -r requirements.txt
```

Inspect the LSM layout before patching: 

```bash
python3 query_btf_types.py /path/to/target.btf --name '^lsm_blob_sizes$'
python3 query_btf_types.py /path/to/target.btf --name '^inode_security_struct$'
```

Run a non-writing analysis first: 

```bash
python3 patch_init_boot_ksu_lsm.py \
  /path/to/init_boot.img \
  --btf /path/to/target.btf \
  --output /path/to/init_boot-bridge.img \
  --ko-output /path/to/kernelsu-bridge.ko \
  --dry-run
```

Remove ``--dry-run`` only after checking the reported field offsets, SID store, relocation sites, input hash, and output hash. 

Flash the patched ``init_boot`` to the active slot via fastboot in fastboot mode. Use ``adb reboot bootloader`` to reboot to the bootloader from the desktop, if necessary. 

#### Acceptance testing

After the repair is complete, the following commands can be used to perform a read-only test. 

```powershell
$ok = 0
1..500 | ForEach-Object {
    adb shell -t su -c 'true' 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { $ok++ }
}

"OK=$ok/500"
adb shell cat /proc/uptime
adb shell getprop persist.sys.boot.reason.history
adb shell su -c 'dmesg | grep -E "list_del corruption|selinux_inode_free_security|kernel BUG|Kernel panic|Internal error: Oops|inode security ABI" || true'
```

The criteria for judgment are ``OK=500/500``, uptime continuously increases, no new ``kernel_panic,bug`` is added to the startup history, and dmesg does not have the above signature. 

#### Safety and limits

- The tool never contacts a device or a network service. 
- It expects an AArch64 Android boot header v3/v4 init_boot image with ``kernel_size=0``. 
- It patches relocation addends in place and intentionally refuses to rebuild CPIO metadata or alter the module size. 
- It fails instead of guessing when the module's hard-coded ``sid`` field no longer matches the target BTF. 
- It preserves the AVB footer and partition tail but does not re-sign or regenerate vbmeta. The bootloader must already allow the modified image. 
- A relocation patch is a compatibility workaround. A KMI-matched source build remains the durable fix. 

#### Declaration of GenAI

The code in this directory was generated entirely by GenAI. The analysis of kernel crash causes was primarily led by GenAI with human assistance. 
The documentation was mainly written manually with AI-assisted generation. 
Users should independently review the code on their own devices and decide whether to apply it only after fully understanding the risks. 

---

### LSM Offset Bridge

本目录存储了一些 Python 脚本，用于暂时缓解内核级 root 解决方案因在新布局上使用来自旧 Linux 安全模块（LSM）布局的偏移量而意外写入相邻 inode 列表元数据时引起的内核崩溃。

| Python 脚本 | 用途 |
| - | - |
| ``patch_init_boot_ksu_lsm.py`` | 根据 BTF 定位 KernelSU LSM 重定位并重新打包 init_boot |
| ``extract_btf_types.py`` | 修补器使用的最小 BTF 解析器 |
| ``query_btf_types.py`` | 只读查询 BTF 结构与成员偏移 |
| ``requirements.txt`` | Python 运行依赖 |

**BakaSU 及其它一些 KSU 变体已于 2026 年 10 月 31 日永久修复此问题，详情请参阅 [https://github.com/Baka-SU/BakaSU/commit/f98b7a5b909910e1830cae8a2f9c78a61f1f6c2a](https://github.com/Baka-SU/BakaSU/commit/f98b7a5b909910e1830cae8a2f9c78a61f1f6c2a)。**

#### 现象

设备使用过程中突发整机卡死，屏幕点击在应用内外均无响应，物理按键操作亦无效。约数秒后（通常不超过五秒），屏幕变黑；再经数秒（通常不超过十秒），设备开始引导启动。

用户输入开机密码进入桌面后发现，整机卡死前数十秒内所作的更改未见报错，但均未保存，包括但不限于文件保存、Wi-Fi 状态变更等。

该现象随机出现，但大多数出现在文件读写之后。例如，使用 Swift Backup 执行备份还原，或通过 adb 导出大型的错误日志到电脑上时，很有可能出现此现象。

#### 原因

根据上述现象，初步推测系整机卡死前数十秒内产生的缓存未能持久化至物理存储所致。同时，调取各方崩溃日志进行排查，初步定位为内核崩溃。

故障在一台运行 Linux ``6.6.144-4k-g9bf326ec3b1e`` 的一加 PJZ110 上复现。内核更新加入 ``backing_file`` LSM hook 后，在 ``struct lsm_blob_sizes`` 中间插入了新字段：

```text
旧布局                              新布局

lbs_cred        +0x0                lbs_cred         +0x0
lbs_file        +0x4                lbs_file         +0x4
lbs_inode       +0x8                lbs_backing_file +0x8
lbs_superblock  +0xc                lbs_inode        +0xc
```

设备上的 ``kernelsu.ko`` 仍按旧布局编译。文件包装器中读取的仍然是 ``selinux_blob_sizes + 0x8``，但该位置现在保存的是 ``backing_file`` 的大小，真正的 ``lbs_inode`` 已移到 ``+0xc``。

由于 LSM 会按 8 字节对齐 inode 安全对象，旧偏移得到的地址比实际 ``inode_security_struct`` 早 8 字节。最终，32 位 ``ksu_file_sid`` 被写到：

```text
inode_security_struct + 0x14
= list.prev 的高 32 位
```

这次错误写入不会立刻触发崩溃。直到之后某个受影响的 inode 被释放，``selinux_inode_free_security()`` 调用 ``list_del()`` 时才发现链表指针已经损坏，随后触发内核 BUG，并发生内核崩溃导致的重启。
这也解释了为什么故障会延迟出现，且表现得很随机，以及为什么损坏指针中反复出现 ``0x0000005b``。而它，就是 KernelSU 缓存的文件 SID。

捕获到的内核 panic 调用堆栈如下：

```text
list_del corruption: malformed prev/next pointer
__list_del_entry_valid_or_report
selinux_inode_free_security
security_inode_free
__destroy_inode
evict
iput
dentry_unlink_inode
__dentry_kill
dentry_kill
dput
__fput
__fput_sync
__arm64_sys_close
kernel BUG at lib/list_debug.c
Internal error: Oops - BUG: Fatal exception
Kernel panic - not syncing: Oops - BUG: Fatal exception
```

在这条堆栈中，``close``/``__fput_sync`` 路径是发现者：它在释放 inode 时检测到已经损坏的链表。真正的污染源是前面描述的 ``ksu_file_sid`` 错误写入。

#### 桥

该问题可从两方面着手解决。

- 由内核开发者在现有内核中移除 ``lbs_backing_file`` 字段，以回滚 LSM 布局。但 ROM 编译与发行周期通常较长，且多数内核紧密依赖上游（例如 PixelOS 内核依赖 LineageOS 内核，LineageOS 内核依赖 Linux 内核），LSM 布局原则上不会逆向回退。因此，该方案恐难作为长期根本解决方案。
- 由内核级 root 解决方案适配新的 LSM 布局，并构建更通用的 LSM 定位机制。

理论上，同一大版本（如 6.6）下，内核架构（含 LSM 布局）应保持相对稳定，以减少基于通用内核开发的开发者在细版本（如 6.6.127 与 6.6.144）间的适配成本。但在实践中，内核版本并不承诺同一大版本下 LSM 布局保持不变。

本存储库定位为上述两端之间的过渡桥梁，提供范围有限的过渡性修复。

#### 修复方案

长期方案仍如上文所述。但在相应构建暂时不可用时，本存储库提供的 Python 脚本可利用已由内核级 root 解决方案修补过的 ``init_boot`` 中预先嵌入的内容重定位信息。

修补流程如下：

1. 读取目标内核 BTF，或从包含 BTF 的 Android 内核 ``Image`` 中读取；
2. 解析 ``lsm_blob_sizes.lbs_inode`` 与 ``inode_security_struct.sid``；
3. 从 init_boot 的 ramdisk 中提取 KernelSU 模块；
4. 反汇编 AArch64 可执行段，定位写入 ``sid`` 的 ``str`` 指令；
5. 找到为该指令提供地址的 ``selinux_blob_sizes`` 的 ``ADRP`` 与低 12 位重定位对；
6. 只修改这两个重定位的 addend；
7. 重新压缩 ramdisk，保持 AVB footer 和分区尾部不变，并重新提取验证。

本次复现内核的结果是：

```text
lsm_blob_sizes.lbs_inode       +0x8 -> +0x0c
inode_security_struct.sid      +0x1c
修改的模块重定位               0x8698 与 0x869c
模块实际变化字节               2
```

生成镜像的 SHA-256 为：

```text
490b51443ffb4a5d055b0c128e0ca57c93c17ab9ca32e4af264434abb7271142
```

该镜像刷入 ``_a`` 槽后，与之前验证过的修复镜像逐字节一致。之后使用 0912 内核 BTF 再运行时，工具正确选择 ``lbs_inode=+0x8``，没有修改模块。

## 快速开始

运行环境需要 Python 3.10 或更高版本，并安装 ``capstone``、``pyelftools`` 和 ``lz4``。只有目标 ramdisk 使用 Zstandard 时才需要可选包 ``zstandard``。

```bash
python3 -m pip install -r requirements.txt
```

先检查目标 LSM 结构：

```bash
python3 query_btf_types.py /path/to/target.btf --name '^lsm_blob_sizes$'
python3 query_btf_types.py /path/to/target.btf --name '^inode_security_struct$'
```

先进行不会写入镜像的干跑：

```bash
python3 patch_init_boot_ksu_lsm.py \
  /path/to/init_boot.img \
  --btf /path/to/target.btf \
  --output /path/to/init_boot-bridge.img \
  --ko-output /path/to/kernelsu-bridge.ko \
  --dry-run
```

确认工具报告的字段偏移、SID 写入位置、重定位地址、输入哈希和输出哈希均合理后，再去掉 ``--dry-run`` 生成镜像。

通过 fastboot 模式，使用 fastboot 将已修补的 ``init_boot`` 刷入活动插槽。如有必要，请使用 ``adb reboot bootloader`` 从桌面重启进入引导加载程序。

#### 验收测试

修复完成后，可以用下面的命令执行只读式测试。

```powershell
$ok = 0
1..500 | ForEach-Object {
    adb shell -t su -c 'true' 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { $ok++ }
}

"OK=$ok/500"
adb shell cat /proc/uptime
adb shell getprop persist.sys.boot.reason.history
adb shell su -c 'dmesg | grep -E "list_del corruption|selinux_inode_free_security|kernel BUG|Kernel panic|Internal error: Oops|inode security ABI" || true'
```

判断标准是 ``OK=500/500``、uptime 持续增长、启动历史不新增 ``kernel_panic,bug``，且 dmesg 没有上述签名。

#### 安全边界与限制

- 工具不会连接设备，也不会访问网络服务。
- 只支持 AArch64 Android boot header v3/v4 且 ``kernel_size=0`` 的 init_boot。
- 工具在原位置修改重定位 addend，不会重建 CPIO 元数据，也不会接受大小改变后的模块。
- 如果模块中硬编码的 ``sid`` 字段与目标 BTF 不一致，工具会直接失败，不会猜测后生成不完整修补。
- 工具保留 AVB footer 和分区尾部，但不会重新签名或重新生成 vbmeta；bootloader 必须原本就允许修改后的镜像启动。
- 这只是兼容性修补。与目标 KMI 匹配的源码构建仍是正式且长期的修复方式。

#### 生成式 AI 声明

本目录下的代码全程由 GenAI 生成；内核崩溃原因的分析主要由 GenAI 主导、人工辅助完成；文档主要由人工编写、AI 辅助生成。使用者应在自有设备上独立复核，并在充分理解风险后自行决定是否应用。
