#### Configuration tutorial of HMA and its branches

In LSPosed, only the System Framework should be selected as the scope. After activating the HMAL/HMA with only System Framework as the target (including when HMAL/HMA is updated or downgraded), please be reminded to reboot your device. 

In HMAL/HMA, at least one template should be created first. For example, a blacklist template (official recommended) should be designed, which should include all the applications that should not be detected by others. 
Alternatively, design a whitelist template (user recommended) that should only include general applications. 

Subsequently, go to the application management tab in HMAL/HMA and, for each application that will detect the "TWRP, Magisk, LSPosed, and Plugins" environment, do: 

1) Enable hiding; 
2) Select the blacklist or whitelist template you wish to use; and
3) Configure additional invisible or visible applications (corresponding to the blacklist or whitelist mode) if necessary. 

These two operations can be configured dynamically without rebooting, configuring in LSPosed Manager, or restarting the specified application. 

- If you want to make an application to be seen or not to be seen, just modify the template or the specified configuration for the specified application in HMAL/HMA. 
- If you want to make an application able or unable to see other applications, just go to the application management tab in HMAL/HMA. 

Faithfully speaking, a plugin that can hide the application list without manual configuration would be better. 

- Classifications: 
  - Classification $S$: Unlaunchable system and launchable critical system pre-installed applications; 
  - Classification $B$: LRFP-related applications that need to bypass detection: 
  - Classification $C$: Applications designed for environment detection (the cat and ~~the~~ mouse); and
  - Classification $D$: Plain Android desktop applications (that love detecting environments). 
- Examples: 
  - $S$: ``com.oneplus.coreservice`` and ``com.android.settings``; 
  - $B$: ``io.github.vvb2060.magisk`` and ``com.google.android.hmal``; 
  - $C$: ``com.reveny.nativecheck`` and ``com.zhenxi.hunter``; 
  - $D$: ``com.tencent.mm`` and `` com.tencent.mobileqq``. 
- Configurations: 
  - $U := S \cup B \cup C \cup D$
  - $\forall s \in S$: $s$ should be able to see and be seen by $\forall x, x \in U$; 
  - $\forall b \in B$: $b$ should be able to see $\forall x, x \in U$ and be seen by only $\forall x, x \in S \cup B$; 
  - $\forall c \in C$: $c$ should be able to see $\forall x, x \in S \cup \lbrace c\rbrace \cup D$ and be seen by only $\forall x, x \in S \cup B \cup \lbrace c\rbrace$; 
  - $\forall d \in D$: $d$ should be able to see $\forall x, x \in S \cup D$ and be seen by $\forall x, x \in U$ (note that we do not consider the detection between applications caused by enterprises having severe conflicts of interest with each other or detection from home applications to abroad ones). 
- Accomplishments: 
  - Library: Gather all the lists in a cloud library and generate configurations based on the cloud library (like [https://github.com/LRFP-Team/Bypasser/tree/main/src/webroot/classifications](https://github.com/LRFP-Team/Bypasser/tree/main/src/webroot/classifications)); 
  - Local recognition (difficult to implement and may require artificial intelligence technology): It should belong to $B$ when an application contains an Xposed/Edxposed/LSPosed interface. 

If you want to have a JSON configuration file generated based on the cloud library, please refer to the configuration generation in [https://github.com/LRFP-Team/Bypasser](https://github.com/LRFP-Team/Bypasser). 

This classification method will be updated appropriately in January 2026. 

---

#### 隐藏应用列表及其分支配置教程

在LSPosed中，只应选择系统框架作为范围。在仅以系统框架为目标激活 HMAL/HMA 后（包括 HMAL/HMA 更新或降级时），请记住重新启动您的设备。

在 HMAL/HMA 中，应首先创建至少一个模板。例如，应设计一个黑名单模板（官方推荐），其中应包含所有不希望被其它应用程序检测到的应用程序；或者，设计一个白名单模板（用户推荐），其中应仅包含一般的应用程序。

随后，转到 HMAL/HMA 中的应用程序管理，对于将检测“TWRP，Magisk，LSPosed 和 Plugins”环境的每个应用程序，执行：

1) 启用隐藏；
2) 选择要使用的黑名单或白名单模板；
3) 如有需要，配置额外不可见或可见的应用程序（分别对应黑名单或白名单模式）。

这两个操作可以动态配置，而无需重新启动，在 LSPosed 管理器中配置或重新启动指定的应用程序。

- 如果您想让应用程序可见或不可见，只需修改 HMAL/HMA 中指定应用程序的模板或指定配置即可。
- 如果您想让某个应用程序能够或无法看到其他应用程序，只需转到 HMAL/HMA 中的应用程序管理页面。

事实上，或许一个不需要手动配置就能够完成应用列表隐藏的插件会更好。

- 分类：
  - 分类 $S$：无法启动的系统应用和可启动的关键系统预装应用；
  - 分类 $B$：需要过检的 LRFP 相关应用；
  - 分类 $C$：用于环境检测的应用（既是猫又是老鼠）；
  - 分类 $D$：（热衷于检测环境的）普通安卓桌面应用。
- 示例：
  - $S$: ``com.oneplus.coreservice`` 和 ``com.android.settings``；
  - $B$: ``io.github.vvb2060.magisk`` 和 ``com.google.android.hmal``；
  - $C$: ``com.reveny.nativecheck`` 和 ``com.zhenxi.hunter``；
  - $D$: ``com.tencent.mm`` 和 `` com.tencent.mobileqq``. 
- 配置：
  - $U := S \cup B \cup C \cup D$
  - $\forall s \in S$：$s$ 应当能够检测到并被 $\forall x, x \in U$ 检测到；
  - $\forall b \in B$：$b$ 应当能够检测到 $\forall x, x \in S \cup B \cup C \cup D$，但仅能够被 $\forall x, x \in S \cup B$ 检测到；
  - $\forall c \in C$：$c$ 应当能够检测到 $\forall x, x \in S \cup \lbrace c\rbrace \cup D$，但仅能够被 $\forall x, x \in S \cup B \cup \lbrace c\rbrace$ 检测到；
  - $\forall d \in D$：$d$ 应当能够检测到 $\forall x, x \in S \cup D$，但能够被 $\forall x, x \in U$ 检测到（此处不考虑由企业利益冲突引发的相互检测以及境内软件对境外软件的检测）。
- 实现：
  - 库：将分类上传到云库中并基于云库下发配置（例如 [https://github.com/LRFP-Team/Bypasser/tree/main/src/webroot/classifications](https://github.com/LRFP-Team/Bypasser/tree/main/src/webroot/classifications)）；
  - 本地识别（实现较为困难且可能需要人工智能技术）：识别到插件接口时应当自动归类为 $B$。

如果你希望拥有一个基于云库下发的 JSON 配置文件，请参阅 [https://github.com/LRFP-Team/Bypasser](https://github.com/LRFP-Team/Bypasser) 中的配置文件生成。

此分类方法会在 2026 年 1 月进行一次合理的更新。
