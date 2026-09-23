### Rooting

This folder aims to archive the latest versions of different Magisk, Apatch (AP), and KernelSU (KSU), along with their variants. 

Please also consider using the latest one generated in the ``Actions`` tab of the corresponding GitHub repository if open-source. 

Variants within the same series are enumerated in ascending order of founding date. 
Kernel files and spoofed managers (non-archived) in KSU and its variants would not be stored here to reduce the repository size. 
As KSU and some of its variants have inconsistent version codes in their GitHub workflows, 
only the version in the latest successful workflow triggered by the ``push`` will be stored here for all KSU and its variants. 

- Magisk and its variants 
  - Magisk / Magisk Beta / Magisk Canary / Magisk Debug: [https://github.com/topjohnwu/Magisk](https://github.com/topjohnwu/Magisk)
  - Magisk Alpha (closed-source)
    - [https://t.me/magiskalpha](https://t.me/magiskalpha)
  - Magisk Delta / Kitsune Magisk (built-in whitelist mode): [https://github.com/HuskyDG/magisk-files](https://github.com/HuskyDG/magisk-files)
- Apatch: [https://github.com/bmax121/APatch](https://github.com/bmax121/APatch) and [https://t.me/APatchChannel](https://t.me/APatchChannel)
- KernelSU and its variants 
  - KernelSU
    - [https://github.com/tiann/KernelSU](https://github.com/tiann/KernelSU)
    - [https://t.me/KernelSU](https://t.me/KernelSU)
  - KernelSU Next (KSUN)
    - [https://github.com/KernelSU-Next/KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next)
    - [https://t.me/ksunext_ci](https://t.me/ksunext_ci)
  - SukiSU-Ultra: [https://github.com/SukiSU-Ultra/SukiSU-Ultra](https://github.com/SukiSU-Ultra/SukiSU-Ultra)
    - ReSukiSU (forked from SukiSU-Ultra): [https://github.com/ReSukiSU/ReSukiSU](https://github.com/ReSukiSU/ReSukiSU)
  - Wild KSU (WKSU): [https://github.com/WildKernels/Wild_KSU](https://github.com/WildKernels/Wild_KSU)

Among the three series, Magisk and its variants are user-space-level rooting solutions and cannot bypass the dirty SELinux policy detection. The others are kernel-level ones. 
Version 31000 of Magisk and its variants change the terminal behavior. For example, it directly uses the system's ``sh``, making classic code such as ``< <(getevent -ql)`` unusable. 
Versions below 31000 of Magisk and its variants, APatch and its variants, and KernelSU and its variants, all use shell interpreters that support the aforementioned features. 
In addition, different root managers behave differently regarding whether they automatically close the window after executing an action. 

Currently, almost all GKI device users are using KSU and its variants as the root implementation. 
As the most original root solution that modifies the ``boot`` partition to achieve rooting without physically modifying the ``system`` partition, 
Magisk and its variants remain the most widely used root implementation method due to their general applicability. 

[Riru](./Modules/Riru) and Zygisk(./Modules/Zygisk) are two important fundamental rooting-layer system modules that offer rich application programming interfaces (APIs) to other system modules or plugins. 
Compared to Riru, Zygisk allows Magisk to run within Zygote, offering more precise control, better performance, and greater concealment. 

Compared with Magisk and its variants, KSU and its variants themselves do not mount the ``/system`` partition, making the environment detectors harder to detect the rooting environments. 
Nonetheless, some modules (e.g., those that install applications as system ones) need to mount the ``/system`` partition to make modifications on it. 
In the ZIP file (the installer used in the root manager) of such a module, there is normally a folder named ``system`` under the root of the module folder after unzipping the ZIP. 
[Metamodules](./Modules/Metamodules) are designed to support such modules in KSU and its variants. 
That is to say, metamodules will control the installation of the rooting-layer system modules if any one of them is installed. 

---

### Root 层

本文件夹旨在存储不同 Magisk、Apatch（AP）和 KernelSU（KSU）以及它们的变体的最新版本。

对于开源存储库，请一并考虑使用相应 GitHub 存储库中 ``Actions`` 选项卡里的最新版本。

同一系列的变体按创始日期升序枚举。
为了减少存储库的大小，KSU 及其变体中的内核文件和混淆管理器（未归档的）将不会存储在此处。
由于 KSU 及其部分变体在其不同的 GitHub 工作流中的版本号不一致，
此处统一对 KSU 及其所有变体仅保存由 ``push`` 事件触发的最新成功工作流中的版本。

- 面具及其变体
  - 面具 / Beta 版面具 / 金丝雀面具 / Debug 版面具：[https://github.com/topjohnwu/Magisk](https://github.com/topjohnwu/Magisk)
  - 阿尔法面具（闭源）
    - [https://t.me/magiskalpha](https://t.me/magiskalpha)
  - 德尔塔面具 / 小狐狸面具（内置白名单模式）：[https://github.com/HuskyDG/magisk-files](https://github.com/HuskyDG/magisk-files)
- Apatch：[https://github.com/bmax121/APatch](https://github.com/bmax121/APatch) 和 [https://t.me/APatchChannel](https://t.me/APatchChannel)
- KernelSU 及其变体
  - KernelSU
    - [https://github.com/tiann/KernelSU](https://github.com/tiann/KernelSU)
    - [https://t.me/KernelSU](https://t.me/KernelSU)
  - KernelSU Next（KSUN）
    - [https://github.com/KernelSU-Next/KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next)
    - [https://t.me/ksunext_ci](https://t.me/ksunext_ci)
  - SukiSU-Ultra：[https://github.com/SukiSU-Ultra/SukiSU-Ultra](https://github.com/SukiSU-Ultra/SukiSU-Ultra)
    - ReSukiSU（SukiSU-Ultra 的下游）：[https://github.com/ReSukiSU/ReSukiSU](https://github.com/ReSukiSU/ReSukiSU)
  - Wild KSU（WKSU）：[https://github.com/WildKernels/Wild_KSU](https://github.com/WildKernels/Wild_KSU)

在这三个系列中，Magisk 及其变体是用户空间级别的 root 解决方案，无法规避脏 SELinux 策略检测。其它系列则是内核级别的 root 解决方案。
Magisk 及其变体的 31000 版本修改了终端行为，例如，直接使用系统的 sh，使得 ``< <(getevent -ql)`` 等经典代码无法使用。
Magisk 及其变体的 31000 以下版本、Apatch 及其变体和 KSU 及其变体等均使用支持上述特性的 shell 解释器。
此外，不同的 root 管理器在执行 action 后是否自动关闭窗口的行为有所不同。

目前，GKI 设备的用户几乎都在使用 KSU 及其变体作为 root 实现方案。
由于通用性最强，作为最原始的通过修补 ``boot`` 分区以在不实际修改 ``system`` 分区的情况下实现 root 的 root 实现方案，Magisk 及其变体目前仍然是使用人数最多的 root 实现方案。

[Riru](./Riru) 和 [Zygisk](./Zygisk) 是两个重要的基础 root 层系统模块，为其它系统模块或插件提供丰富的应用程序编程接口 (API)。
相比于 Riru，Zygisk 让 Magisk 运行在 Zygote 中，拥有更精确的控制、更好的性能和更强的隐蔽性。

与 Magisk 及其变体不同，KSU 及其变体本身并不挂载 ``/system`` 分区，这能够让环境检测器更难检测到 root 环境。
然而，某些模块（例如，那些将应用程序安装为系统程序的模块）需要挂载 ``/system`` 分区才能对其进行修改。
在此类模块的 ZIP 文件（用于在 root 管理器中刷入的模块安装包）中，我们通常能够在解压后的模块文件夹的根目录下找到一个名为 ``system`` 的非空文件夹。
KSU 及其衍生版本中的[元模块](./Modules/Metamodules)旨在支持此类模块。
这也意味着，如果安装了元模块（只能安装一个），它们将控制 root 层系统模块的安装行为。
