### Low-level

The bottom layer, from "top" to "bottom", can be listed as follows. From top to low, the low-level can be listed as follows. Please note that within the system, the higher the privileges, 
the greater the capabilities, and the heavier the responsibilities; outside the system, the lower the level, the greater the capabilities, and the heavier the responsibilities. 

- system: This includes normal booting, safe-mode booting, root, root core mode (all modules are suspended), modules, frameworks, plugins, and applications
- recovery: This is the mode where flashing from recovery and adb sideload can be conducted (Use files of type ``.zip`` with Android recovery mode operations or the adb tool)
- fastbootd: This is the dynamic mode of fastboot on Android 10 and above to dynamically operate logical partitions within the ``super`` partition 
(Use files of type ``.img`` named as the logical partition within the ``super`` partition with the fastboot tool)
- fastboot: This is the mode where USB flashing and temporary booting can be conducted (Use files of type ``.img`` with the fastboot tool)
- bootloader: This is the mode where USB flashing and temporary booting can be conducted (Use files of type ``.img`` with the fastboot tool)
- deep flashing: This is the mode where deep flashing, like 9008, can be conducted (Use files like ``.ops`` that include detailed partition information with tools like MSM that can force downloading)
- flashback: Conduct motherboard flashback (Use files that include detailed motherboard information with high-voltage power supply cable, forced download cable, and tools supporting motherboard programming)

Unless otherwise specified, the tools mentioned above are generally used on a personal computer with appropriate drivers installed. 

The following is a list of LRFP-related faults from less severe to more severe. It is feasible to use methods for repairing more severe faults to repair less severe faults, 
but this is generally not recommended. After all, data should be saved if possible. The more severe the fault, the fewer free resources there are, and the more difficult it is to do it ourselves. 

- bootloop caused by a module (the local data can normally be saved)
  - restore the stock boot/init_boot via USB flashing, 
  - enter a third-party recovery to disable or remove the causing module(s), or 
  - Wait to enter the root core mode after three failed boot attempts to boot into the system to disable or remove the causing module(s)
- bootloop caused by flashing a patched image: fastboot the stock partition back (the local data can normally be saved)
- able to boot to the bootloader but unable to flash one or more partitions: This most likely indicates a corrupted partition table that requires a deep flash (the local data can hardly be saved)
- a crash message appears but cannot boot to the bootloader after pressing and holding the power button to power on: A deep flash is required (the local data can hardly be saved)
- the battery has power but nothing happens after pressing and holding the power button (the local data can hardly be saved)
  - this should be caused due to the self-protection of the motherboard
  - flashback the motherboard if the motherboard is not physically damaged
  - conduct the deep flashing after the motherboard is fixed
- physical motherboard damage: Buy a new motherboard or a new Android device (the local data can hardly be saved)
- motherboard and other hardware damage physically: Buy new hardware that is broken or a new Android device (the local data can hardly be saved)

For users who are using the OnePlus 13 series, please refer to [https://roms.danielspringer.at/](https://roms.danielspringer.at/). 

---

### 底层

底层，自“顶”向“底”可做出如下列举。请注意，在系统中，权限越高，能力越大，责任越重；在系统外，越底层，能力越大，责任越重。

- 系统：系统正常模式、系统安全模式、root、root 安全模式（临时停用所有模块仅加载核心功能）、模块、框架、插件和应用等都在此范围内
- 恢复模式（recovery）：卡刷和 adb 侧载（adb sideload）在此进行（使用 ``.zip`` 类型的文件并配以安卓恢复模式的操作或 adb 工具）
- 适用于动态分区结构的 fastboot 模式（fastbootd）：用于安卓 10 及以上对 ``super`` 分区内的逻辑分区进行动态操作（使用以 ``super`` 分区内的逻辑分区为名的 ``.img`` 文件并配以 fastboot 工具）
- 快速引导模式/快速启动模式/刷机模式（fastboot）：线刷和临时启动通常在此进行（使用 ``.img`` 类型的文件并配以 fastboot 工具）
- 引导加载程序（bootloader）：线刷和临时启动通常在此进行（使用 ``.img`` 类型的文件并配以 fastboot 工具）
- 深刷：形如 9008 的深刷救砖（使用形如 ``.ops`` 的包含详细分区信息的原厂深刷文件并配以形如 MSM 的具有强制下载功能的工具）
- 烧录：烧录主板（使用包含详细主板信息的原厂烧录文件并配以高压供电线、强制下载线和具有主板烧录功能的工具）

如无特别说明，上述的工具一般在装有适当驱动的个人电脑上使用。

自不严重向严重对 LRFP 有关的故障列举如下，当然，使用用于修复更为严重的故障的方式来修复较为不严重的故障是可行的，但一般不这么做，毕竟能救数据就救数据，且越往后免费资源越少越难自己动手。

- 某一模块导致无法开机：线刷还原原厂 boot/init_boot、进入第三方恢复禁用相关模块或等待某些 root 方案在三次开机失败后进入 root 安全模式后开机进入系统禁用相关模块（一般不会丢失本地数据）
- 修补某一原厂镜像刷入后无法开机：对对应分区线刷（不用深刷）对应分区的原厂镜像即可（一般不会丢失本地数据）
- 能进入引导加载程序但无法线刷某一个或多个分区：大概率是分区表被破坏了只能深刷（会丢失本地数据）
- 长按电源键开机后直接显示崩溃信息无法进入引导加载程序：深刷（会丢失本地数据）
- 电池有电但长按电源键手机完全没有反应：如果主板没硬件坏大概率是触发了主板的电路保护需要烧录主板后深刷（会丢失本地数据）
- 主板损坏：更换主板或更换手机（会丢失本地数据）
- 主板及其它硬件损坏：更换硬件或换手机（会丢失本地数据）

对于一加 13 系列的用户，您可以访问 [https://roms.danielspringer.at/]https://roms.danielspringer.at/)。
