### Special Cases

If some applications still detect LRFP-related environments or exhibit issues that only occur on devices with LRFP environments after following the [general guidelines](./README.md), please refer to this document. 

#### Momo

##### Package management service exception

Turn off "Disable package manager signature verification" in Core Patcher by referring to [a post in early 2023](https://zhidao.baidu.com/question/633770792883881924.html)

##### Debugging mode is enabled

- Turn off the debugging mode when not in use
- It is not recommended to use plugins for bypassing because it will expose Xposed/Edxposed/LSPosed injection/hooks (confidence level), which is not worth the loss, though injecting the detection application can pass the debug mode (suspicious level)

##### Detect the existence of TWRP file(s)

Rename the TWRP folder under ``/sdcard/`` (for example, .TWRP)

##### Unlocked bootloader

- Install [Play Integrity fix](https://github.com/KOWX712/PlayIntegrityFix/actions) module
- It is not recommended to use plugins for bypassing because it will expose Xposed/Edxposed/LSPosed injection/hooks (confidence level), which is not worth the loss, though the injection of the detected application can pass the debug mode (suspicious level)

#### Ruru

##### Found HMA in ``syscall``

- Before June 24th, 2025: Switch to HMAL
- On or after June 24th, 2025: Install the latest HMA plugin

#### Native Root Detector

##### Detected Abnormal Environment (with a number with six decimal places as the detail)

- Update the Zygisk Next module to 1.3.0 and later. 
- Enable both anonymous memory and the Zygisk Next linker, or disable both of them in the Zygisk Next module. 

##### Detected Zygisk

Update the Zygisk Next module to 1.3.0 and later. 

##### LSPosed traces are detected in the ``odex`` file of GMS or this application

- Backup your plugin configurations in the LSPosed manager settings
- Uninstall Native Root Detector totally
- Disable WeChat and QQ (via Swift Backup or Fridge) if necessary
- Uninstall the original LSPosed in the root manager and reboot your device
- Install the lastest build in [https://github.com/JingMatrix/LSPosed/actions](https://github.com/JingMatrix/LSPosed/actions) in the root manager and reboot your device
- Restore your plugin configurations in the LSPosed manager settings
- Switch to the plugin tab of the LSPosed manager to check whether the restoration of all plugin configurations is finished
- Reboot your device
- Install the latest Native Root Detector for detection (do not restore Native Root Detector from any backup)
- Enable WeChat and QQ only after the detector shows normal environments (except risky applications detected with Code 3)

##### Mount inconsistency detected / Magic Mount Detected

- Magisk and its branches: Use Magisk Alpha and install the latest Shamiko module
- Apatch and its branches: Embed the Cherish Peekaboo module as a kernel module (please check if the ``compat`` version is needed)
- KSU and its branches: Use SukiSU-Ultra and Install the latest SUSFS module as a system module

##### Risky application detected (bypassed HMA and its branches with Code 3)

The logic of this detection is to start an activity of the target application under Android 13. This detection is handled by ``HMA_v3.5`` from June 24th, 2025. 

##### Risky application detected (bypassed HMA and its branches with Code 4)

The logic of this detection is to find folders named by the application package names recorded in the library under certain specific directories. Please try to check whether there is a folder named by the listed package names found by the detector in ``/sdcard/Android/data``. If the folder is empty, you can try to delete it. 
If necessary, please assign the listed application package names found by the detector to the variable ``packageNames`` with a space character as the separator. Subsequently, execute the following script as a non-root user to observe which folders named by the package names can be detected by applications without root permissions. 

```
#!/system/bin/sh
readonly EXIT_SUCCESS=0
readonly EXIT_FAILURE=1
exitCode=${EXIT_SUCCESS}
folders="/data/data /data/user/0 /data/user_de/0 /sdcard/Android/data"
packageNames="com.rifsxd.ksunext com.sukisu.ultra com.topjohnwu.magisk io.github.huskydg.magisk io.github.vvb2060.magisk me.bmax.apatch me.garfieldhan.apatch.next me.weishu.kernelsu"
for packageName in ${packageNames}
do
	for folder in ${folders}
	do
		if [[ -e "${folder}/${packageName}" ]];
		then
			exitCode=${EXIT_FAILURE}
			echo "Found \"${folder}/${packageName}\". "
		fi
	done
done
exit ${exitCode}
```

#### Native Test

##### Native Test reports ``Malicious Hook`` on some devices, whether there are LRFP environments

It is said by many people that this is a false negative result. 

##### Others

Please refer to [https://bbs.kanxue.com/thread-285106-1.htm](https://bbs.kanxue.com/thread-285106-1.htm)

#### Bankings

##### The Postal Savings Bank application still crashes after using the latest official Magisk and the latest Shamiko module at that time, around September 2023

- Caused by historical issues, updating can solve the problem
- For users of Magisk and its branches
  - If you were using Magisk and its branches around September 2023, please install the latest Magisk Delta and enable the whitelist mode
  - If you were using Magisk and its branches between October 2023 and the discontinuation of Magisk Delta, please install the latest Magisk Alpha and the latest Shamiko module, or install the latest Magisk Delta and enable the whitelist mode
  - If you were using Magisk and its branches between the discontinuation of Magisk Delta and the release of Zygisk Next version 1.3.0, please install the latest Magisk Alpha and the latest Shamiko module
  - If you are currently using the official Magisk and its branches, please install the latest Magisk Alpha and the latest Zygisk Next module and enable ``Treat non-root apps as denylist`` with ``just_umount`` in the Zygisk Next module

##### The Bank of China (Hong Kong) (BOCHK) application is unable to perform biometric authentication after upgrading its security measures on December 21st, 2025

- Remove the package name of the BOCHK application from the target of the Tricky Store module
- If biometric authentication is still unavailable, try resetting your BOCHK mobile security password or clearing all data of the BOCHK application

#### 12306

##### Cannot use the face recognition

Ask your ROM developer to sign the ROM when building

#### Social Software from Mainland China

##### Sending device risk alerts, deactivating users, restricting social features, or freezing accounts

- Mobile QQ (Android)
  - The definition of downgrading: Do not expose any suspicious environment (including root and injection environment) or perform any injection to QQ and use the core patcher plugin to downgrade QQ after 15 days (and observe for another 15 days)
  - If you are using a QQ version at or below ``v8.6.0``
    - Never upgrade the QQ until the update is a must
    - Upgrade to the minimum version above the current version if the update is a must
  - If you are using a QQ version within the interval (``v8.6.0``, ``v8.8.17``] that is affected by the 2021 spring and summer risk control event (the phenomenon is most obvious when using the ``v8.8.0`` version)
    - If you want to use the QXposed (QX) plugin or the QQ Repeater plugin while you can still downgrade your QQ
      - Switch to the ``v8.6.0`` or lower version (if rollback is still allowed)
    - Otherwise
      - Uninstall the QXposed (QX) plugin and the QQ Repeater plugin
      - Disable the red envelope grabbing, automatic group sign-in, and the group messaging functions
      - Uninstall any QQ plugin that is not adapted to the Xposed API calling protection of LSPosed
  - If you are using a QQ version within the interval (``v8.8.17``, ``v8.9.56``]
    - Never upgrade the QQ until the update is a must
    - Upgrade to the minimum version above the current version if the update is a must
    - Uninstall the QXposed (QX) plugin and the QQ Repeater plugin
    - Disable the red envelope grabbing, automatic group sign-in, and the group messaging functions
    - Uninstall any QQ plugin that is not adapted to the Xposed API calling protection of LSPosed
  - If you are using a QQ version above ``v8.9.56`` that is affected by the 2024 autumn to 2025 spring risk control event (the phenomenon is most obvious when using the ``v9.1.35`` version)
    - Please refer to the issues mentioned in (``v8.8.17``, ``v8.9.56``]
    - If you want to use the XAutoDaily (XA) plugin or the QAuxiliary (QA) plugin while you can still downgrade your QQ
      - Make sure that you have already hidden the rooting and injection environments according to the common procedures shown in this page
      - In the QAuxiliary (QA) plugin, turn on the "disable QQ hot patch" switch and turn off the "environment detection package (trpc.o3.*) interception" switch
      - Switch to the ``v9.1.31`` or lower versions, 
      - Switch to the ``v9.0.95`` or lower versions, or
      - Switch to the ``v8.9.56`` or lower versions (if accepting non-NT architecture)
    - Otherwise
      - Uninstall all the QQ plugins
      - Disable the red envelope grabbing, automatic group sign-in, and the group messaging functions
      - Do not expose any suspicious environment (including root and injection environment) or perform any injection to QQ (remember to disable QQ in advance when switching environments) when using versions above ``v9.1.31``
- Computer QQ (Windows): Always use the nostalgic version instead of the QQNT version

##### Failed to open the fingerprint payment prompt (but other domestic and foreign applications can use fingerprints normally)

- Temporary solution: Use the WeChat Payment module or the WeChat Payment plugin (the principle is to submit the pre-stored password after passing the fingerprint)
- Essential solution: None

##### Speculations about social media applications sending device risk alerts, deactivating users, restricting social features, or freezing accounts

Although some "LRFP" enthusiasts claim that WeChat and QQ restrictions are unrelated to their versions, with a detailed quantitative computation method proposed, our personal perspective is that the higher the version, the more "cold" code there is locally for environment detection, and the richer the support for "hot" code sent from the cloud for environment detection. 

For a long time, members of our team were often deactivated and restricted the next day after upgrading to a certain version during the major risk control periods. Downgrading to a version below that level only resulted in a warning, and downgrading to an even lower version or below eliminated any warnings, where, if the warnings were caused by the device ID being previously uploaded to the cloud, replacing the device is necessary. 

Furthermore, Android application-layer injection has been proven impossible to bypass by any third-party means. As long as the injected application wants to detect the injection, it can succeed. Secure bypassing is only possible by "controlling" all environment detection-related code within the target application while injecting. This requires plugin developers to conduct in-depth reverse engineering of the target application and make bold assumptions about the cloud. 

---

### 特殊情况

如在按照[通用流程](./README.md)部署后某些应用程序仍然检测到与 LRFP 相关的环境或出现仅在具有 LRFP 环境的设备上出现的问题，可尝试参阅本文档。

#### Momo

##### 包管理服务异常

在核心破解中关闭“禁用软件包管理器签名验证”（参考自[一篇 2023 年初的问答](https://zhidao.baidu.com/question/633770792883881924.html)）

##### 已开启调试模式

- 在不使用调试模式时关闭调试模式
- 不建议使用插件进行过检因为对检测应用注入虽然能够过检掉调试模式（可疑级别）但会暴露 Xposed/Edxposed/LSPosed 注入/钩子（确信级别）反而得不偿失

##### 存在 TWRP 文件

将 ``/sdcard/`` 下的 TWRP 文件夹重命名（例如 .TWRP）

##### Bootloader 未锁定

- 在面具层安装最新版 [Play Integrity fix](https://github.com/KOWX712/PlayIntegrityFix/actions) 模块
- 不建议使用插件进行过检因为对检测应用注入虽然能够过检掉调试模式（可疑级别）但会暴露 Xposed/Edxposed/LSPosed 注入/钩子（确信级别）反而得不偿失

#### Ruru

##### ``syscall`` 找到 HMA

- 2025 年 6 月 24 日前：换用 HMAL
- 2025 年 6 月 25 日及之后：安装最新版 HMA 插件

#### Native Root Detector

##### 检测到环境异常（以一个包含六个小数位的数字作为详情）

- 将 Zygisk Next 模块升级至 1.3.0 或更高。
- 在 Zygisk Next 模块中同时启用或同时禁用匿名内存和 Zygisk Next linker。

##### 检测到 Zygisk

将 Zygisk Next 模块升级至 1.3.0 或更高。

##### 检测到 GMS 或本应用的的 ``odex`` 文件中存在 LSPosed 痕迹

- 在 LSPosed 管理器设置中备份您的插件配置
- 彻底卸载 Native Root Detector
- 如有必要请禁用微信和 QQ（可通过 Swift Backup 或冰箱应用）
- 在 root 管理器中卸载原版 LSPosed 并重启设备
- 在 root 管理器中安装最新版 [https://github.com/JingMatrix/LSPosed/actions](https://github.com/JingMatrix/LSPosed/actions) 中的最新版本并重启设备
- 在 LSPosed 管理器设置中恢复您的插件配置
- 切换到 LSPosed 管理器的“插件”选项卡，检查所有插件配置是否已恢复完成
- 重启设备
- 安装最新的 Native Root Detector 进行检测（请勿从任何备份中恢复 Native Root Detector）
- 仅该检测器显示环境正常（以代码 3 显示的检测到风险应用除外）后才可以重新启用微信和 QQ

##### 检测到挂载不一致 / 检测到 Magic Mount

- Magisk 系列：使用 Magisk Alpha 并安装最新版 Shamiko 模块
- Apatch 系列：以内核模块的形式嵌入 Cherish Peekaboo 模块（请自行排查是否需要 compat 版本）
- KSU 系列：使用 SukiSU-Ultra 并安装最新版 SUSFS 模块

##### 检测到风险应用（绕过 HMA 及其分支的代码 3）

该检测适用于安卓 13 以下的操作系统，通过启动目标应用的 Activity 实现检测，已于 2025 年 6 月 25 日在 ``HMA_v3.5.r449.1d951a3 (449)`` 中得到修复。

##### 检测到风险应用（绕过 HMA 及其分支的代码 4）

该检测原理为找到了某些特定目录下存在以与库中记录的应用包名命名的文件夹，请尝试查看 ``/sdcard/Android/data`` 下是否存在以所列出包名命名的文件夹，如果该文件夹为空可尝试将其删除；
如有必要，请将所列出的应用包名以空格为分隔符赋值为变量 ``packageNames``，随后以普通用户身份执行以下脚本观察无 root 权限的应用可以检测到哪些以包名命名的文件夹。

```
#!/system/bin/sh
readonly EXIT_SUCCESS=0
readonly EXIT_FAILURE=1
exitCode=${EXIT_SUCCESS}
folders="/data/data /data/user/0 /data/user_de/0 /sdcard/Android/data"
packageNames="com.rifsxd.ksunext com.sukisu.ultra com.topjohnwu.magisk io.github.huskydg.magisk io.github.vvb2060.magisk me.bmax.apatch me.garfieldhan.apatch.next me.weishu.kernelsu"
for packageName in ${packageNames}
do
	for folder in ${folders}
	do
		if [[ -e "${folder}/${packageName}" ]];
		then
			exitCode=${EXIT_FAILURE}
			echo "Found \"${folder}/${packageName}\". "
		fi
	done
done
exit ${exitCode}
```

#### 牛头人

##### Native Test 在某些无论是否有 LRFP 环境的设备上报 ``Malicious Hook``

大多数人认为这是误报。

##### 其它问题

请参阅 [https://bbs.kanxue.com/thread-285106-1.htm](https://bbs.kanxue.com/thread-285106-1.htm)

#### 银行类应用程序

##### 2023 年 9 月左右使用了当时最新版官方面具和最新版 Shamiko 后打开邮储银行依旧直接闪退

- 由历史问题引起，更新即可解决问题
- 对于使用 Magisk 及其分支的用户
  - 如果您在 2023 年 9 月左右使用 Magisk 及其分支，请使用最新的 Magisk Delta 并打开白名单模式
  - 如果您在 2023 年 10 月与 Magisk Delta 停更之间使用 Magisk 及其分支，请安装最新的 Magisk Alpha 和最新的 Shamiko 模块，或安装最新的 Magisk Delta 并打开白名单模式
  - 如果您在 Magisk Delta 停更与 Zygisk Next 1.3.0 版本发布之间使用 Magisk 及其分支，请安装最新的 Magisk Alpha 和最新的 Shamiko 模块
  - 如果您现在正在使用官方 Magisk 及其分支，请安装最新的 Magisk Alpha 和最新的 Zygisk Next 模块并在 Zygisk Next 中启用将非 root 应用视为排除列表和仅还原挂载

##### 中银香港应用程序在 2025 年 12 月 21 日升级了保安措施后无法进行生物认证

- 从 Tricky Store 模块的 target 中移除中银香港应用程序的包名
- 如果仍然无法进行生物认证可尝试重设流动保安密码或清除中银香港应用程序的所有数据

#### 12306

##### 无法使用人脸识别

请让您的 ROM 开发者在编译时对 ROM 进行签名

#### 中国大陆社交软件

##### QQ 无故发送设备风险提醒、下线用户、限制社交功能或冻结账号

- 手机 QQ（安卓版）
  - 定义降级：不向 QQ 暴露任何可疑环境（含 root 和注入环境）或执行任何注入 15 天后利用核心破解插件降级 QQ（后再观察 15 天）
  - 如果您使用的 QQ 版本低于 ``v8.6.0``
    - 除非被云控强制升级否则请勿升级 QQ
    - 如被云控强制升级请升级到高于当前版本的最低版本
  - 如果您使用的 QQ 版本处于 2021 年春夏季节风控事件影响区间 (``v8.6.0``, ``v8.8.17``) 内（此现象在使用 ``v8.8.0`` 版本时最为明显）
    - 如果您想继续使用 QXposed（QX）插件或 QQ 复读机插件且 QQ 能够降级
      - 请切换到 ``v8.6.0`` 或更低版本
    - 否则
      - 请卸载 QXposed（QX）插件或 QQ 复读机插件
      - 请禁用抢红包、自动群签到和消息群发功能
      - 请卸载所有不适配 LSPosed 的 Xposed API 调用保护的 QQ 插件
  - 如果您使用的 QQ 版本处于 (``v8.8.17``, ``v8.9.56``] 区间内
    - 除非被云控强制升级否则请勿升级 QQ
    - 如被云控强制升级请升级到高于当前版本的最低版本
    - 请卸载 QXposed（QX）插件或 QQ 复读机插件
    - 请禁用抢红包、自动群签到和消息群发功能
    - 请卸载所有不适配 LSPosed 的 Xposed API 调用保护的 QQ 插件
  - 如果您使用的 QQ 版本高于 ``v8.9.56`` 且受 2024 年秋季至 2025 年春季风控事件影响（使用 ``v9.1.35`` 版本时现象最为明显）
    - 请参阅 (``v8.8.17``, ``v8.9.56``]
    - 如果您想使用 XAutoDaily（XA）插件或 QAuxiliary（QA）插件，并且仍然可以降级您的 QQ，请
      - 确保您已按照本页的通用流程隐藏 root 和注入环境
      - 在 QAuxiliary（QA）插件中打开禁用 QQ 热补丁开关并关闭环境检测包（trpc.o3.*）拦截开关
      - 切换到 ``v9.1.31`` 或更低版本，
      - 切换到 ``v9.0.95`` 或更低版本，或者
      - 切换到 ``v8.9.56`` 或更低版本（如果接受非 NT 架构）
    - 否则
      - 请卸载所有 QQ 插件
      - 请禁用抢红包、自动群签到和消息群发功能
      - 高于 ``v9.1.31`` 版本时切勿向 QQ 暴露（切换环境时记得提前禁用 QQ）任何可疑环境（含 root 和注入环境）或执行任何注入
- 电脑 QQ（Windows）：始终使用最新怀旧版而非 QQNT 版本

##### 微信开启指纹支付提示失败（但其它境内外应用都能正常使用指纹）

- 临时解决方法：使用微信支付模块或微信支付插件（原理是通过指纹后将预先存储的密码进行提交）
- 本质解决方法：暂无

##### 关于社交软件发送设备风险提醒、下线用户、限制社交功能或冻结账号的猜测

虽然部分“LRFP”爱好者表示微信和 QQ 的限制与版本无关，并总结出了一套详细的量化的计算公式，但个人感觉是版本越高，本地用于检测环境的“冷”代码就越多，对云端下发的用于检测环境的“热”代码的支持就越丰富。

长期以来，本团队中的成员经常在大型风控期间一越过某个版本第二天就被下线和限制，而降级至该版本以下就只会收到警告，再降级到某个更低的版本或以下就不再收到任何警告（当然如果之前是因为设备 ID 已经被上传到了云端而收到不断下发的警告则需要更换设备后警告才会被消除）。

另外，安卓应用层注入已被证明无法通过任何第三方手段对被注入的应用程序进行隐藏，只要被注入的应用程序想检测，就有手段检测到；只有在注入目标应用时将目标应用内所有与环境检测有关的代码“控制”住才可能实现安全的隐藏，而这，需要插件的开发人员对目标应用进行极为深入的逆向分析以及对云端的大胆揣测。
