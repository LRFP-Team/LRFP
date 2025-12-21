### Rooting

This folder aims to archive the latest versions of different Magisk, Apatch (AP), and KernelSU (KSU) branches. 

Please also consider using the latest one generated in the ``Actions`` tab of the corresponding GitHub repository if open-source. 

Branches within the same series are enumerated in ascending order of time. As there are many kernel files in KSU and its branches, they would not be stored here. 

- Magisk and its branches 
  - Magisk / Magisk Beta / Magisk Canary / Magisk Debug: [https://github.com/topjohnwu/Magisk](https://github.com/topjohnwu/Magisk)
  - Magisk Alpha (closed-source)
    - [https://github.com/CoderTyn/Magisk-Alpha](https://github.com/CoderTyn/Magisk-Alpha)
    - [https://install.appcenter.ms/users/vvb2060/apps/magisk/distribution_groups/public](https://install.appcenter.ms/users/vvb2060/apps/magisk/distribution_groups/public)
    - [https://t.me/magiskalpha](https://t.me/magiskalpha)
  - Magisk Delta / Kitsune Magisk (built-in whitelist mode): [https://github.com/HuskyDG/magisk-files](https://github.com/HuskyDG/magisk-files)
- Apatch: [https://github.com/bmax121/APatch](https://github.com/bmax121/APatch) and [https://t.me/APatchChannel](https://t.me/APatchChannel)
- KernelSU and its branches 
  - KernelSU
    - [https://github.com/tiann/KernelSU](https://github.com/tiann/KernelSU)
    - [https://t.me/KernelSU](https://t.me/KernelSU)
  - KernelSU Next (KSUN)
    - [https://github.com/KernelSU-Next/KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next)
    - [https://t.me/ksunext_ci](https://t.me/ksunext_ci)
  - SukiSU Ultra: [https://github.com/SukiSU-Ultra/SukiSU-Ultra](https://github.com/SukiSU-Ultra/SukiSU-Ultra)

Among the three series, Magisk and its branches are user-space-level rooting solutions, and the others are kernel-level ones. 

Currently, almost all GKI device users are using KSU and its branches as the root implementation. 

As the most original root solution that modifies the ``boot`` partition to achieve rooting without physically modifying the ``system`` partition, 
Magisk and its branches remain the most widely used root implementation method due to their general applicability. 

[Riru](./Riru) and Zygisk(./Zygisk) are two important fundamental rooting-layer system modules that offer rich application programming interfaces (APIs) to other system modules or plugins. 

Compared to Riru, Zygisk allows Magisk to run within Zygote, offering more precise control, better performance, and greater concealment. 

---

### Root 层

本文件夹旨在存储不同 Magisk、Apatch (AP) 和 KernelSU (KSU) 分支的最新版本。

对于开源存储库，请一并考虑使用相应 GitHub 存储库中 ``Actions`` 选项卡里的最新版本。

同一系列的分支按时间顺序升序枚举；由于 KSU 及其分支的内核文件太多，此处不存储此类文件。

- 面具及其分支
  - 面具 / Beta 版面具 / 金丝雀面具 / Debug 版面具：[https://github.com/topjohnwu/Magisk](https://github.com/topjohnwu/Magisk)
  - 阿尔法面具（闭源）
    - [https://github.com/CoderTyn/Magisk-Alpha](https://github.com/CoderTyn/Magisk-Alpha)
    - [https://install.appcenter.ms/users/vvb2060/apps/magisk/distribution_groups/public](https://install.appcenter.ms/users/vvb2060/apps/magisk/distribution_groups/public)
    - [https://t.me/magiskalpha](https://t.me/magiskalpha)
  - 德尔塔面具 / 小狐狸面具（内置白名单模式）：[https://github.com/HuskyDG/magisk-files](https://github.com/HuskyDG/magisk-files)
- Apatch：[https://github.com/bmax121/APatch](https://github.com/bmax121/APatch) 和 [https://t.me/APatchChannel](https://t.me/APatchChannel)
- KernelSU 及其分支
  - KernelSU
    - [https://github.com/tiann/KernelSU](https://github.com/tiann/KernelSU)
    - [https://t.me/KernelSU](https://t.me/KernelSU)
  - KernelSU Next（KSUN）
    - [https://github.com/KernelSU-Next/KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next)
    - [https://t.me/ksunext_ci](https://t.me/ksunext_ci)
  - SukiSU Ultra：[https://github.com/SukiSU-Ultra/SukiSU-Ultra](https://github.com/SukiSU-Ultra/SukiSU-Ultra)

在这三个系列中，Magisk 及其分支是用户空间级别的 root 解决方案，而其他系列是内核级别的 root 解决方案。

目前，GKI 设备的用户几乎都在使用 KSU 及其分支作为 root 实现方案。

由于通用性最强且作为最原始的通过修补 ``boot`` 分区以在不实际修改 ``system`` 分区的情况下实现 root 的 root 实现方案，Magisk 及其分支目前仍然是使用人数最多的 root 实现方案。

[Riru](./Riru) 和 [Zygisk](./Zygisk) 是两个重要的基础 root 层系统模块，为其它系统模块或插件提供丰富的应用程序编程接口 (API)。

相比于 Riru，Zygisk 让 Magisk 运行在 Zygote 中，拥有更精确的控制、更好的性能和更强的隐蔽性。
