---
source: https://blog.csdn.net/allen_xu_2012_new/article/details/131167564
title: "Android Activity启动过程详解"
collected_at: 2026-03-21
tags: [Android, Framework, Activity, AMS, Zygote, 启动流程]
references:
  - https://blog.csdn.net/allen_xu_2012_new/article/details/131167564
---

# Android Activity 启动过程详解

> 来源：CSDN | 作者：allen_xu_2012_new

---

## 一、两种启动类型

1. **startActivity() 启动**：在 Activity 中调用 `startActivity(Intent)`
2. **Launcher 启动**：点击桌面图标启动 App（流程更全面复杂）

---

## 二、启动流程五大阶段

```
┌─────────────────────────────────────────────────────────────┐
│  阶段1: Launcher → ATMS                                    │
│  点击图标，请求 ATMS 启动应用                                │
├─────────────────────────────────────────────────────────────┤
│  阶段2: ATMS → AMS                                          │
│  ATMS 向 AMS 发送创建应用进程请求                           │
├─────────────────────────────────────────────────────────────┤
│  阶段3: AMS → Zygote                                        │
│  AMS 向 Zygote 发送创建进程请求                             │
├─────────────────────────────────────────────────────────────┤
│  阶段4: Zygote fork                                         │
│  Zygote 接收请求，fork 并启动应用进程 ActivityThread        │
├─────────────────────────────────────────────────────────────┤
│  阶段5: ActivityThread 启动 Activity                        │
│  应用进程启动并展示 Activity                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、详细流程

### 阶段 2.1：调用 ATMS 系统进程

#### Launcher 桌面入口

```xml
<!-- Launcher3 AndroidManifest.xml -->
<activity
    android:name="com.android.launcher3.Launcher"
    android:launchMode="singleTask"
    android:clearTaskOnLaunch="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.HOME" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
</activity>
```

#### 关键方法调用链

```
startActivitySafely()
    ↓
execStartActivity()
    ↓
ATMS.startActivity()
```

---

### 阶段 2.2：ATMS 向 AMS 发送创建应用进程

#### 核心组件

| 组件 | 作用 |
|------|------|
| ActivityTaskManagerService (ATMS) | 任务管理服务 |
| ActivityStartController | 启动控制器 |
| ActivityStarter | 启动执行器 |
| RootWindowContainer | 窗口容器根节点 |
| ActivityStack | Activity 栈管理 |
| ActivityStackSupervisor | 栈监督器 |

#### 流程

```
ATMS.startActivity()
    ↓
ActivityStartController.obtainInstance()
    ↓
ActivityStarter.execute()
    ↓
RootWindowContainer.resumeFocusedTasks()
    ↓
ActivityStack.startActivity()
    ↓
ActivityStackSupervisor.startSpecificActivity()
```

---

### 阶段 2.3：AMS 向 Zygote 发送创建进程请求

#### 核心组件

| 组件 | 作用 |
|------|------|
| ActivityManagerService (AMS) | 进程管理服务 |
| ProcessList | 进程列表管理 |
| Process | 进程管理 |
| ZygoteProcess | Zygote 进程通信 |
| Zygote | 孵化进程 |

#### 流程

```
AMS.getContentProvider()
    ↓
Process.start()
    ↓
ZygoteProcess.start()
    ↓
ZygoteProcess.attemptZygoteSendArgs()
    ↓
ZygoteState.connect()  // 建立 Socket 连接
```

---

### 阶段 2.4：Zygote fork 并启动应用进程

#### 核心方法调用链

```
ZygoteServer.runSelectLoop()      // 监听 Socket
    ↓
ZygoteConnection.processOneCommand()  // 处理请求
    ↓
Zygote.forkAndSpecialize()      // fork 子进程
    ↓
handleChildProc()               // 处理子进程
    ↓
zygoteInit()                    // 初始化
    ↓
RuntimeInit.applicationInit()   // 应用初始化
    ↓
MethodAndArgsCaller.run()       // 启动 ActivityThread
```

---

### 阶段 2.5：ActivityThread 启动 Activity

#### 核心组件

| 组件 | 作用 |
|------|------|
| ActivityThread | 应用主线程 |
| ApplicationThread | 与 AMS 通信的 Binder |
| ClientTransaction | 事务管理 |
| TransactionExecutor | 事务执行器 |
| LaunchActivityItem | 启动 Activity 事务 |

#### 流程

```
AMS.bindApplication()
    ↓
ActivityThread.handleBindApplication()
    ↓
mApplication.onCreate()
    ↓
ATMS.attachApplication()
    ↓
RootWindowContainer.attach()
    ↓
ClientTransaction.schedule()
    ↓
TransactionExecutor.execute()
    ↓
LaunchActivityItem.execute()
    ↓
ActivityThread.handleLaunchActivity()
    ↓
Activity.onCreate()
```

---

## 四、关键类总结

| 类 | 层级 | 职责 |
|----|------|------|
| Launcher | App | 桌面入口 |
| ATMS | System | 任务管理 |
| AMS | System | 进程管理 |
| Zygote | Native | 进程孵化 |
| ActivityThread | App | 应用主线程 |
| ApplicationThread | App | AMS 通信 |
| ClientTransaction | IPC | 事务封装 |
| TransactionExecutor | IPC | 事务执行 |

---

## 五、LaunchActivityItem 执行的生命周期

```
onCreate() → onStart() → onResume()
```

事务转换时会按照状态机执行对应的生命周期方法。
