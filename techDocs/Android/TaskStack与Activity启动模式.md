---
source: 
  - https://blog.csdn.net/u013718730/article/details/108362585
  - MotoCarLink 车机投屏项目内部技术分析文档
title: "【Android】【TaskStack】任务栈与 Activity 启动模式全解析（含虚拟屏场景）"
collected_at: 2026-03-28
tags: [Android, TaskStack, Activity, LaunchMode, VirtualDisplay, 启动模式, 投屏]
references:
  - https://blog.csdn.net/u013718730/article/details/108362585
---

# Android 任务栈与 Activity 启动模式全解析

> 来源：CSDN + MotoCarLink 车机投屏项目内部技术分析 | 合并整理

---

## 一、什么是任务栈（Task Stack）

### 1.1 基础定义

任务栈是**管理 Activity 切换**的数据结构（栈结构），记录了 Activity 之间的调用和启动顺序。

按下返回键时，根据任务栈信息决定返回到哪个窗口。

### 1.2 核心特性

1. 新 Activity 被放置在**栈顶**，只有栈顶 Activity 可与用户交互
2. 栈顶 Activity 结束后，回退到**上一个 Activity**
3. 任务栈中 Activity 全部结束后，销毁任务栈，回退到最近访问的任务栈
4. **系统桌面（Launcher）也是独立任务栈**
5. 任务栈由**操作系统管理**，不属于某个应用或进程
6. 一个应用可包含**多个任务栈**，一个任务栈也可包含**不同应用的 Activity**

### 1.3 何时创建新任务栈

以下情况会创建新任务栈：
- 通过桌面图标启动新 Activity
- 通过通知栏启动新 Activity
- 旧 Activity 启动 **SingleInstance** 模式 Activity
- 旧 Activity 启动指定了 **taskAffinity** 属性的 Activity
- 旧 Activity 启动 **documentLaunchMode="always"** 的 Activity
- 旧 Activity 启动时指定了 **FLAG_ACTIVITY_NEW_TASK** 选项

---

## 二、Activity 启动模式（LaunchMode）

### 2.1 四种启动模式详解

| 模式 | 行为 | 栈内数量 |
|------|------|----------|
| **Standard** | 默认模式，总是在当前栈中创建新实例 | 多个 |
| **SingleTop** | 栈顶已存在该类实例则复用（调用 onNewIntent），否则新建 | 多个 |
| **SingleTask** | 栈中已存在该类实例则复用，并**弹出栈顶所有在其上方的 Activity** | 唯一 |
| **SingleInstance** | 独占一个任务栈，全局唯一实例 | 唯一（独占栈） |

### 2.2 SingleTask 的清除机制详解

`singleTask` 模式的清除行为是最容易被误解的部分：

- **不是清除整个栈**，而是**清除目标 Activity 之上的所有 Activity**
- 清除后，目标 Activity 成为栈顶，系统调用其 `onNewIntent()` 方法（如果已存在）
- 如果栈中不存在目标 Activity，则在其归属的栈中创建新实例

**示例：**
```
栈状态：A → B → C → D（栈顶），D 为 SingleTask
启动 D → 结果：A → B → C → D（复用，D 回到栈顶，触发 onNewIntent）
```

### 2.3 各模式适用场景

**Standard 模式**
- 场景：普通的内容列表页、新闻feed页
- 效果：每次进入都新建实例，适合可重复访问的页面

**SingleTop 模式**
- 场景：短视频 APP 观看页面，点击推荐视频
- 效果：复用当前播放页面，刷新推荐列表，无需新建实例
- 注意：仅在栈顶时复用，不在栈顶则仍会创建新实例

**SingleTask 模式**
- 场景：购物 APP → 商品页 → 下单页 → 支付页 → 完成
- 效果：返回时销毁下单和支付页面，直接回到商品页
- 典型应用：APP 主页、浏览器 Tab 页

**SingleInstance 模式**
- 场景：系统相机应用、拨打电话、地图导航（不允许同时打开两份）
- 效果：全局单例，独占任务栈，其他应用任何位置启动都会复用同一个实例
- 注意：从该栈返回时，会回到启动它的上一个栈

### 2.4 SingleInstance 的回退问题

当两个任务栈之间启动过其他应用（如按 Home 键），会导致回退混乱。

**问题示例：**
```
栈A（AppA）→ 栈B（SingleInstance相机）→ 按Home → Launcher栈 → 回到栈B → 栈B销毁 → 回到Launcher（桌面）
```

**解决方案：在 Activity 中管理任务栈，将其他任务栈调度至前台**

```java
@Override
public void onBackPressed() {
    ActivityManager manager = getSystemService(ActivityManager.class);
    List<ActivityManager.RunningTaskInfo> infos = manager.getRunningTasks(100);

    for (ActivityManager.RunningTaskInfo info : infos) {
        int taskId = info.id;
        ComponentName topActivity = info.topActivity;
        
        // 跳过当前任务栈
        if (taskId == getTaskId()) continue;
        // 跳过外部任务栈（只处理同包名的任务栈）
        if (!topActivity.getPackageName().equals(getPackageName())) continue;
        
        // 将任务栈调度至前台
        manager.moveTaskToFront(taskId, 0);
        break;
    }
    
    moveTaskToBack(true);
    finishAndRemoveTask();
}
```

---

## 三、Intent Flags 与启动行为控制

### 3.1 核心 Flag 一览

| Flag | 作用 |
|------|------|
| `FLAG_ACTIVITY_NEW_TASK` | 在新任务栈中启动 Activity，等同于设置 `singleTask` 模式 |
| `FLAG_ACTIVITY_SINGLE_TOP` | 如果目标 Activity 在栈顶则复用，等同于 `singleTop` 模式 |
| `FLAG_ACTIVITY_CLEAR_TOP` | 清除目标 Activity 之上的所有 Activity（配合 NEW_TASK 使用效果等同 singleTask） |
| `FLAG_ACTIVITY_CLEAR_TASK` | 启动前先清除目标 Activity 所在任务栈，再启动新 Activity |
| `FLAG_ACTIVITY_REORDER_TO_FRONT` | 将已在栈中的 Activity 移动到栈顶（不清除任何 Activity） |
| `FLAG_ACTIVITY_NO_HISTORY` | 启动后立即离开，Activity 不会留在任务栈中 |
| `FLAG_ACTIVITY_PREVIOUS_IS_TOP` | 用于处理 up navigation 行为 |
| `FLAG_ACTIVITY_RESET_TASK_IF_NEEDED` | 系统自动重置任务栈 |

### 3.2 启动模式与 Intent Flags 的交互优先级

**重要结论：启动模式（launchMode）的优先级高于 Intent Flags**

当同时指定了 `android:launchMode="singleTask"` 和 `FLAG_ACTIVITY_NEW_TASK` 时：
- 系统**优先检查 launchMode**，按 singleTask 规则处理
- `FLAG_ACTIVITY_NEW_TASK` 会被忽略

**singleTask 模式下的跨屏行为：**
- 系统会优先寻找**全局范围内（跨所有显示器/虚拟屏）**是否已存在该 Task
- 如果 App 已经在主屏运行，再次在虚拟屏启动时，系统会执行**任务迁移（Task Migration）**
- 任务迁移将**整个 Task 从主屏移动到虚拟屏**

### 3.3 常用 Flag 组合与业务效果

| Flag 组合 | 业务效果 | 适用场景 |
|----------|---------|----------|
| `NEW_TASK` + `CLEAR_TASK` | **彻底重开**：销毁旧任务栈，冷启动应用 | 投屏 Launcher 切换 App（最推荐） |
| `NEW_TASK` + `REORDER_TO_FRONT` | **无损平移**：将任务栈整体搬移，保留页面状态 | 希望保留手机端操作进度时 |
| `NEW_TASK` + `CLEAR_TOP` | **栈内复用**：清空上方页面，触发 onNewIntent，回到首页 | 内部页面跳转 |
| `NEW_TASK` + `CLEAR_TOP` + `SINGLE_TOP` | 模拟 `singleTask` 行为：复用旧任务，清除顶部所有页面 | 对未设置 singleTask 的应用进行行为模拟 |
| `SINGLE_TOP` | **顶部复用**：栈顶已存在则复用，触发 onNewIntent | 避免重复创建同一页面 |

### 3.4 各组合详细行为

**FLAG_ACTIVITY_NEW_TASK + FLAG_ACTIVITY_CLEAR_TASK（推荐用于投屏 App 切换）**

```kotlin
val intent = Intent().apply {
    component = ComponentName(packageName, activityName)
    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
}
startActivity(intent)
```

- 效果：先强制销毁目标应用在当前 Display 上的已有任务栈，然后以冷启动方式在当前 Display 重新创建任务栈
- 优点：确保应用重新检查当前 Display 的分辨率和屏幕方向（Configuration Changes），保证 UI 适配正确
- 场景：车机投屏中从一个 App 切换到另一个 App

**FLAG_ACTIVITY_NEW_TASK + FLAG_ACTIVITY_REORDER_TO_FRONT**

```kotlin
val intent = Intent().apply {
    component = ComponentName(packageName, activityName)
    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_REORDER_TO_FRONT)
}
startActivity(intent)
```

- 效果：将目标应用的任务栈**整体移动**到前台，保留所有页面的操作状态
- 优点：用户切走再切回来时可以继续之前的操作
- 注意：如果目标应用在当前 Display 没有任务栈，则效果等同于 NEW_TASK + CLEAR_TASK

**FLAG_ACTIVITY_NEW_TASK + FLAG_ACTIVITY_CLEAR_TOP**

```kotlin
val intent = Intent().apply {
    component = ComponentName(packageName, activityName)
    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
}
startActivity(intent)
```

- 效果：清除目标 Activity 之上的所有页面，触发目标 Activity 的 `onNewIntent()`
- 如果目标 Activity 不在栈中，则创建新实例
- 场景：App 内部从子页面返回到主页（Home Activity）

**FLAG_ACTIVITY_NEW_TASK + FLAG_ACTIVITY_CLEAR_TOP + FLAG_ACTIVITY_SINGLE_TOP**

```kotlin
val intent = Intent().apply {
    component = ComponentName(packageName, activityName)
    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP)
}
startActivity(intent)
```

- 效果：手动模拟 `singleTask` 行为
- 系统行为：查找全局是否有该 Activity 实例 → 找到 → 弹出其上方所有 Activity → 调用 onNewIntent
- 适用场景：对未在 AndroidManifest 中声明 launchMode 的 Activity 进行 singleTask 行为的动态控制

---

## 四、任务栈高级属性（AndroidManifest）

在 `AndroidManifest.xml` 中配置：

```xml
<activity
    android:name=".ThirdActivity"
    android:taskAffinity=":xxx_task"
    android:documentLaunchMode="always"
    android:allowTaskReparenting="true|false"
    android:alwaysRetainTaskState="true|false"
    android:clearTaskOnLaunch="true|false"
    android:autoRemoveFromRecents="true|false"
/>
```

| 属性 | 作用 | 值 |
|------|------|-----|
| **taskAffinity** | 指定任务栈亲和性，相同 affinity 的 Activity 会放置在同一任务栈 | 字符串，如 `":my_task"` |
| **documentLaunchMode** | 文档模式启动行为 | `always`（每次都新栈）/ `never` / `intoExisting` / `none` |
| **allowTaskReparenting** | 允许 Activity 从启动它的任务栈迁移到同应用的另一个任务栈 | `true` / `false` |
| **alwaysRetainTaskState** | 后台清理时是否保留任务栈状态 | `true` / `false` |
| **clearTaskOnLaunch** | 点击桌面图标重载时是否清理任务栈 | `true` / `false` |
| **autoRemoveFromRecents** | 任务栈为空时是否自动从最近任务列表移除 | `true` / `false` |

### taskAffinity 实战：控制任务栈结构

**场景：** Activity 顺序 X → A → B → C → D → E → X，若希望第二次启动 X 时销毁 D、E，保留 A、B、C

**方法：** 将 X、D、E 设置为相同的 `taskAffinity`，X 设置为 `singleTask` 模式

```
结果栈结构：
Task1: A → B → C（保留）
Task2: X → D → E（X 复用并清除上方 D、E）
```

### documentLaunchMode 详解

| 值 | 行为 |
|----|------|
| `always` | 每次启动都创建新任务栈，在最近任务列表中独立显示 |
| `never` | 不为文档创建新任务栈（默认） |
| `intoExisting` | 如果文档任务栈已存在则复用，否则创建新栈 |
| `none` | 与 `never` 相同 |

---

## 五、虚拟屏（VirtualDisplay）与多屏任务栈

### 5.1 多屏架构概述

Android 支持多屏显示，每个显示设备（Physical Display 或 Virtual Display）在系统内部由独立的 **DisplayContent** 管理。

**核心机制：** 每个 `VirtualDisplay` 都拥有一个逻辑上独立的**任务堆栈（Task Stack List）**。

```
DisplayManagerService
└── DisplayContent（主屏）
    └── Task Stack List
        ├── Task A (Launcher)
        └── Task B (当前前台App)
└── DisplayContent（VirtualDisplay 1 - 投屏）
    └── Task Stack List
        ├── Task C (投屏App A)
        └── Task D (投屏App B)
```

### 5.2 虚拟屏任务栈的独立性与行为

当通过 `ActivityOptions.setLaunchDisplayId(displayId)` 在特定显示器启动 Activity 时：

1. **Activity 绑定到目标显示器**：该 Activity 及其所属的 Task 会绑定到指定 displayId 的显示器
2. **原栈保留**：原有的 Activity 会被压入该显示器的栈底，进入 `onStop()` 状态，但**不会被销毁**
3. **栈持久性**：除非显式调用 `finish()` 或任务被移除，否则该任务栈会一直驻留在该虚拟屏上
4. **跨屏不共享**：主屏和虚拟屏的任务栈**完全独立**，`singleTask` 不会跨屏寻找已有任务

### 5.3 Task Stacking（任务叠加）

使用 `FLAG_ACTIVITY_NEW_TASK` 启动不同包名的 App 时，系统会为每个 App 创建一个独立的 `Task` 实例，并按启动顺序在该虚拟屏上堆叠：

```
VirtualDisplay (DisplayContent)
└── Task Stack
    ├── Task B: New App (Top, Active, 与用户交互)
    └── Task A: Previous App (Stopped, 后台，不可见)
```

**状态说明：**
- **Active Task**：栈顶，完全可见，可与用户交互
- **Stopped Task**：非栈顶，完全不可见（`onStop()` 状态），但未销毁

### 5.4 虚拟屏下 singleTask 的特殊行为

**重要发现：** `singleTask` 模式的优先级高于 `FLAG_ACTIVITY_NEW_TASK`。

- **全局查找**：系统会优先在**全局范围（跨所有显示器）**寻找是否已存在该 Task
- **任务迁移（Task Migration）**：如果 App 已经在主屏运行，再次在虚拟屏启动时，系统会将**整个 Task 从主屏移动到虚拟屏**
- **迁移后果**：主屏上该 App 的任务栈消失，所有页面状态丢失

**场景示例：**
```
主屏：Task A（App:youtube）→ youtube 在主屏打开详情页
投屏：用户打开 youtube → 系统检测到 singleTask → 将 Task A 从主屏迁移到投屏 → 主屏 youtube 栈消失
```

### 5.5 投屏场景下的任务堆积问题

#### 问题根源

在车机投屏等场景下，如果**不主动干预**，虚拟屏的任务栈会随着用户切换应用而不断堆深：

```
VirtualDisplay Task Stack（堆积后）:
├── Task E: 最近启动的App
├── Task D: 第二个App
├── Task C: 第三个App
├── Task B: 第四个App
└── Task A: 第一个App（最早启动，已Stop）
```

#### 具体危害

1. **内存占用增加**：大量后台 Task 持续占用系统资源
2. **交互混乱**：用户在虚拟屏按下返回键时，会意外看到之前启动过的 App，而不是回到 Launcher 桌面
3. **UI 适配问题**：切换回早期 App 时，其 Activity 可能未正确响应屏幕分辨率变化（Configuration 未刷新）

#### 解决方案：启动新应用前清理 Display 任务栈

**方法一：使用 ActivityManager.removeTask（需要系统权限）**

```kotlin
private fun clearTasksOnDisplay(displayId: Int) {
    val am = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
    try {
        val runningTasks = am.getRunningTasks(100)
        for (taskInfo in runningTasks) {
            if (taskInfo.displayId == displayId) {
                // 使用反射调用隐藏 API
                val method = am.javaClass.getMethod(
                    "removeTask",
                    Int::class.javaPrimitiveType
                )
                method.invoke(am, taskInfo.id)
            }
        }
    } catch (e: Exception) {
        Log.e(TAG, "Failed to clear tasks on display $displayId", e)
    }
}
```

**方法二：使用 AppTask.finishAndRemoveTask（应用自身任务）**

```kotlin
val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
val tasks = activityManager.appTasks

for (task in tasks) {
    val taskInfo = task.taskInfo
    if (taskInfo.displayId == targetDisplayId) {
        task.finishAndRemoveTask()
    }
}
```

**方法三：使用 Intent.FLAG_ACTIVITY_CLEAR_TASK（推荐，用于切换目标App）**

```kotlin
val intent = Intent().apply {
    component = ComponentName(targetPackage, targetActivity)
    addFlags(
        Intent.FLAG_ACTIVITY_NEW_TASK or
        Intent.FLAG_ACTIVITY_CLEAR_TASK
    )
}
// 可指定启动的 Display
val options = ActivityOptions.makeMainOptionsMap(displayId)
startActivity(intent, options)
```

### 5.6 跨 Display 的 Activity 操作

#### 设置启动目标 Display

```kotlin
// 方法1：ActivityOptions
val options = ActivityOptions.makeMainOptionsMap(displayId)
startActivity(intent, options)

// 方法2：Intent.setLaunchDisplayId
intent.setLaunchDisplayId(displayId)
startActivity(intent)

// 方法3：ActivityOptions.setLaunchDisplayId
val options = ActivityOptions.newBuilder()
    .setLaunchDisplayId(displayId)
    .build()
startActivity(intent, options)
```

#### 获取当前 Activity 所在的 DisplayId

```kotlin
val displayId = activity.display?.displayId ?: INVALID_DISPLAY

// 或者通过 WindowManager
val windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
val displayId = windowManager.defaultDisplay.displayId
```

#### 将任务栈移动到不同 Display

```kotlin
val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager

// 移动任务到指定 Display
activityManager.moveTaskToFront(
    taskId,
    ActivityManager.MOVE_TASK_WITH_HOME, // 或 MOVE_TASK_NO_USER_ACTION
    Bundle().apply {
        putInt(Intent.EXTRA_TASK_DISPLAY_ID, targetDisplayId)
    }
)
```

---

## 六、任务栈信息获取与操作

### 6.1 AppTask（推荐方式）

```java
ActivityManager activityManager = getSystemService(Context.ACTIVITY_SERVICE.class);
List<ActivityManager.AppTask> tasks = activityManager.getAppTasks();

for (ActivityManager.AppTask task : tasks) {
    ActivityManager.RecentTaskInfo info = task.getTaskInfo();
    
    int taskId = info.id;                      // 任务ID
    Intent launchIntent = info.baseIntent;     // 启动Intent
    int activityCount = info.numActivities;   // Activity数量
    String topActivity = info.topActivity.getClassName();     // 栈顶Activity
    String baseActivity = info.baseActivity.getClassName();  // 任务根Activity
    boolean isRunning = info.isRunning;        // 是否正在运行
    
    // 调度至前台
    task.moveToFront();
    
    // 销毁任务栈内全部Activity并移除任务
    task.finishAndRemoveTask();
}
```

### 6.2 RunningTaskInfo

```java
ActivityManager manager = getSystemService(Context.ACTIVITY_SERVICE.class);
List<ActivityManager.RunningTaskInfo> infos = manager.getRunningTasks(100);

for (ActivityManager.RunningTaskInfo info : infos) {
    int taskId = info.id;                      // 任务ID
    ComponentName baseActivity = info.baseActivity;  // 根Activity
    ComponentName topActivity = info.topActivity;    // 栈顶Activity
    int displayId = info.displayId;            // 所属Display ID
    int numActivities = info.numActivities;     // 栈中Activity数量
    
    // 移动任务到前台
    manager.moveTaskToFront(taskId, 0);
}
```

### 6.3 获取应用自身任务栈

```kotlin
// 获取当前Activity所属任务信息
val taskId = activity.taskId
val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager

// 通过AppTask方式
val appTasks = activityManager.appTasks
for (task in appTasks) {
    if (task.taskInfo.id == taskId) {
        task.moveToFront()
        // 或 task.finishAndRemoveTask()
    }
}
```

---

## 七、常见问题与解决方案

### 7.1 点击桌面图标重启而非恢复

**原因：** 桌面点击图标时，Launcher 检查 Standard 任务栈是否存在来决定启动哪个 Activity

**现象：** App 在后台时，点击桌面图标不是恢复到最后状态，而是重新创建新的 Activity 实例

**解决方案：** 判断应用是首次启动还是二次启动

```java
// 在Application中记录启动时间
long applicationStartTime = System.currentTimeMillis();

// 在 Launcher Activity 中判断
long interval = System.currentTimeMillis() - applicationStartTime;
if (interval > 1000) {
    // 二次启动：销毁SplashActivity和LoginActivity，直接跳到主页
    finish();
    start(MainActivity.class);
}
```

### 7.2 退出时清除最近任务列表缩略图

**场景：** App 退出后，在最近任务列表中仍能看到 App 截图（隐私问题）

```java
@Override
protected void onDestroy() {
    super.onDestroy();
    
    ActivityManager manager = getSystemService(Context.ACTIVITY_SERVICE.class);
    List<ActivityManager.AppTask> tasks = manager.getAppTasks();
    
    for (ActivityManager.AppTask task : tasks) {
        ActivityManager.RecentTaskInfo info = task.getTaskInfo();
        // 只处理没有Activity的任务栈（即已完全退出的）
        if (info.numActivities == 0) {
            task.finishAndRemoveTask();
        }
    }
}
```

### 7.3 投屏时应用未重新检查屏幕配置

**问题：** 从竖屏手机投屏到横屏车机时，应用 UI 未正确旋转

**原因：** 应用未重新触发 Configuration Changes（配置变更检测）

**解决方案：** 使用 `FLAG_ACTIVITY_NEW_TASK + FLAG_ACTIVITY_CLEAR_TASK` 组合启动

- 该组合会强制应用重新检查目标 Display 的分辨率和屏幕方向
- 应用会重新走 `onCreate()` 的配置检测流程

### 7.4 投屏后返回键行为异常

**问题：** 按返回键后看到的不是 Launcher，而是之前启动过的 App

**原因：** 虚拟屏任务栈有多层 Task 堆积，按返回键只是弹出栈顶 Activity

**解决方案：** 参考本文 5.5 节，**在启动新 App 前清理该 Display 的任务栈**，确保返回键行为正确

### 7.5 投屏任务栈残留导致内存占用

**问题：** 长时间使用后，虚拟屏上残留大量已不可见但未销毁的 Task

**解决方案：**
1. 在 Launcher 中维护一个白名单，需要保活的任务栈 ID 记录
2. 每次切换 App 前，先清理不在白名单中的所有 Task
3. 定期（如每小时）检查并清理孤儿 Task

---

## 八、点击桌面图标与 Activity 启动流程详解

### 8.1 Standard 模式下的启动流程

```
用户点击桌面图标
  → Launcher AMS.startActivity()
    → 检查: 目标App已有Standard栈?
      → 有: 在该栈顶创建新Activity实例
      → 无: 创建新任务栈，创建Activity实例
```

### 8.2 SingleTask 模式下的启动流程

```
用户点击桌面图标
  → Launcher AMS.startActivity()
    → 检查: 目标App全局是否有SingleTask Activity实例?
      → 有: 
        → 检查实例所在栈中是否有其他Activity
          → 有: 弹出实例上方所有Activity
          → 无: 保持栈不变
        → 调用实例.onNewIntent()
        → 将该栈调度到前台
      → 无: 在目标位置创建新任务栈和Activity实例
```

### 8.3 Intent Flag NEW_TASK 的启动流程

```
FLAG_ACTIVITY_NEW_TASK
  → 检查: 目标Activity是否已有亲和性相同的栈?
    → 有: 在该栈中启动（行为取决于其他Flag和launchMode）
    → 无: 创建新任务栈，在新栈中启动
```

---

## 九、最佳实践总结

### 9.1 常规 App 开发

| 场景 | 推荐方案 |
|------|----------|
| APP 主页/入口页 | `singleTask`，确保全局唯一实例 |
| 视频播放页、详情页 | `singleTop`，避免重复创建 |
| 需要多实例的页面 | `standard` |
| 系统级应用（相机、电话） | `singleInstance` |

### 9.2 投屏/车机场景

| 场景 | 推荐方案 |
|------|----------|
| 投屏 Launcher 切换 App | `FLAG_ACTIVITY_NEW_TASK + FLAG_ACTIVITY_CLEAR_TASK`，彻底重开，确保 UI 适配 |
| 保留用户操作进度 | `FLAG_ACTIVITY_NEW_TASK + FLAG_ACTIVITY_REORDER_TO_FRONT` |
| App 内返回首页 | `FLAG_ACTIVITY_NEW_TASK + FLAG_ACTIVITY_CLEAR_TOP` |
| 启动前清理旧任务栈 | `ActivityManager.removeTask()` 或反射调用 |
| 动态模拟 singleTask | `NEW_TASK + CLEAR_TOP + SINGLE_TOP` |

### 9.3 虚拟屏任务栈管理策略

1. **确定性原则**：在车机投屏场景下，为了确保 UI 适配（横竖屏切换）和状态洁净，推荐在 `openApp` 之前先**清空该 Display 的已有任务栈**。

2. **启动策略**：使用 `FLAG_ACTIVITY_NEW_TASK` + `FLAG_ACTIVITY_CLEAR_TASK` 组合启动应用，强制应用针对虚拟屏的分辨率进行重新配置检查（Configuration Changes）。

3. **权限要求**：操作任务栈需要 `android.permission.REMOVE_TASKS` 权限，建议 Launcher 应用作为**系统签名应用**运行。

4. **内存管理**：定期清理孤儿任务栈，避免长时间运行后内存占用过高。

5. **返回键白名单**：在 Launcher 中实现返回键拦截逻辑，只有当栈中只剩 Launcher 自己时才响应返回键退出投屏模式。

---

## 十、总结对照表

### 启动模式对比

| 模式 | 栈行为 | 全局唯一 | 适用场景 |
|------|--------|----------|----------|
| **Standard** | 每次新建实例 | ❌ | 普通页面 |
| **SingleTop** | 栈顶复用 | ❌ | 避免重复创建（如视频播放页） |
| **SingleTask** | 清除顶部复用 | ✅（栈内） | 程序入口（如主页） |
| **SingleInstance** | 独占任务栈 | ✅（全局） | 全局单例（如相机、拨打电话） |

### Intent Flags 核心对比

| Flag 组合 | 与 launchMode 的关系 | 清除已有栈 | 清除顶部Activity | 保留状态 |
|-----------|---------------------|-----------|----------------|----------|
| `NEW_TASK` | 动态设置，同 singleTask | ❌ | ❌ | ✅ |
| `NEW_TASK + CLEAR_TASK` | 动态设置，强力重开 | ✅ | ✅ | ❌ |
| `NEW_TASK + CLEAR_TOP` | 动态设置，复用并清除 | ❌ | ✅ | 部分 |
| `NEW_TASK + REORDER_TO_FRONT` | 动态设置，平移 | ❌ | ❌ | ✅ |
| `NEW_TASK + CLEAR_TOP + SINGLE_TOP` | 模拟 singleTask | ❌ | ✅ | 部分 |

**核心理解：** 栈结构并不允许直接复用栈中间的对象，只能复用栈顶对象（SingleTop），或先弹出顶部对象再复用（SingleTask），因此 SingleInstance 只能独占任务栈。在多屏场景下，每个 Display 有独立的任务栈，跨屏启动时系统可能触发任务迁移（Task Migration），这一点在投屏开发中需要特别注意。
