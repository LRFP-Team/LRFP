#### Metamodules

Since KernelSU and its variants do not mount system partitions themselves, users need to install metamodules to support rooting-level system modules that require system partition mounting. 
Therefore, compared with other rooting solutions, metamodules are a unique feature of KernelSU and its variants. 

There are many metamodules designed to provide system partition mounting support for rooting-level system modules, with the following three being the main examples. 

- [OverlayFS](https://github.com/KernelSU-Modules-Repo/meta-overlayfs): This is the officially recommended classic metamodule, utilizing the Linux kernel's OverlayFS mechanism for lossless system modification. 
- [NoMount](https://github.com/maxsteeel/nomount): A mountless metamodule that operates purely at the kernel VFS layer, performing path redirection entirely in RAM without creating any real mounts or polluting ``/proc/mounts``. 
- Magic Mount: Based on the traditional Magic Mount logic, this metamodule is suitable for older environments that do not support OverlayFS. 
  - [Magic Mount](https://github.com/7a72/meta-magic_mount): This repository is the original one but seemed to have been removed from GitHub. 
  - [Magic Mount RS](https://github.com/KernelSU-Modules-Repo/magic_mount_rs)
- [Hybrid Mount](https://github.com/Hybrid-Mount/meta-hybrid_mount): This metamodule works in the hybrid mount mode, but is considered unstable and power-consuming. 

Normally, there is no need to modify ``/system``. Please install a metamodule only if necessary. 
Please note that [some standalone C++ programs under Bypasser](https://github.com/LRFP-Team/Bypasser/tree/main/cpp) may not work correctly when NoMount is active. 

---

#### 元模块

由于 KernelSU 及其变体自身不会挂载系统分区，用户需要安装元模块来支持有系统分区挂载行为的 root 层系统模块。
因此，与其它 root 方案相比，元模块是独属于 KernelSU 及其变体的特性。

用以实现为 root 层系统模块提供系统分区挂载支持的元模块有很多，这里主要列举如下三种。

- [OverlayFS](https://github.com/KernelSU-Modules-Repo/meta-overlayfs)：这是官方推荐的经典元模块，利用 Linux 内核的 OverlayFS 机制进行无损系统修改。
- [NoMount](https://github.com/maxsteeel/nomount)：一个无需挂载的元模块，完全在内核 VFS 层运行，完全在 RAM 中执行路径重定向，而不会创建任何实际挂载点或污染 ``/proc/mounts``。
- Magic Mount：基于传统的 Magic Mount 逻辑，该元模块适用于不支持 OverlayFS 的老旧环境。
  - [Magic Mount](https://github.com/7a72/meta-magic_mount)：此存储库是原始版本，但似乎已从 GitHub 移除。
  - [Magic Mount RS](https://github.com/KernelSU-Modules-Repo/magic_mount_rs)
- [Hybrid Mount](https://github.com/Hybrid-Mount/meta-hybrid_mount)：该元模块以混合挂载模式工作，但目前被认为不稳定且耗电现象明显。

通常情况下不需要修改 ``/system``，因此请仅在必要的情况下安装元模块。
请注意，[Bypasser 下的部分独立 C++ 程序](https://github.com/LRFP-Team/Bypasser/tree/main/cpp)在 NoMount 作用时可能无法正常工作。
