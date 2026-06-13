---
source: https://blog.csdn.net/yanzhenjie1003/article/details/137378331
title: "Android Perfetto Trace性能分析"
collected_at: 2026-03-21
tags: [Android, Perfetto, 性能分析, Trace, 性能优化]
references:
  - https://blog.csdn.net/yanzhenjie1003/article/details/137378331
  - Perfetto 官网: https://perfetto.dev/
  - Perfetto UI: https://ui.perfetto.dev/
  - Python 脚本: https://github.com/google/perfetto/blob/main/tools/record_android_trace
---

# Android Perfetto Trace 性能分析

> 来源：CSDN | 作者：yanzhenjie1003

---

## 一、Perfetto 简介

Perfetto 是 Google 推出的跨平台性能追踪工具，支持：
- Linux、Android、Chrome
- 系统级和应用级活动记录
- 低开销的内存分析（Native + Java）
- Web 可视化界面（Perfetto UI）

---

## 二、生成抓取配置

### 2.1 Perfetto UI 配置流程

1. 打开 [Perfetto UI](https://ui.perfetto.dev/#!/record)
2. 选择目标设备（Android 系统版本 或 ADB 连接设备）
3. 调整 Trace 文件大小和时长
4. 配置探针（Probes）：
   - **CPU**：sched_switch、cpu_frequency、cpu_idle 等
   - **GPU**：gpu_frequency、gpu_mem 等
   - **Power**：电源相关事件
   - **Memory**：内存相关
   - **Android apps**：atrace 配置

### 2.2 配置文件示例

```protobuf
buffers: {
  size_kb: 63488
  fill_policy: DISCARD
}

data_sources: {
  config {
    name: "linux.ftrace"
    ftrace_config {
      ftrace_events: "sched/sched_switch"
      ftrace_events: "sched/sched_wakeup"
      ftrace_events: "power/cpu_frequency"
      ftrace_events: "power/cpu_idle"
      ftrace_events: "gpu_mem/gpu_mem_total"
      atrace_categories: "am"
      atrace_categories: "dalvik"
      atrace_categories: "gfx"
      atrace_categories: "view"
      atrace_apps: "com.example.app"
    }
  }
}

duration_ms: 40000
```

### 2.3 常见问题

- `No field named "cpufreq_period_ms"`：注释掉该行

---

## 三、抓取 Trace 的方式

### 3.1 环境要求

- Android 9 (P) 开始集成
- Android 11 (R) 开始默认开启
- Android 9/10 需要先开启：`adb shell setprop persist.traced.enable 1`

### 3.2 adb 命令抓取

```bash
# 1. 推送配置到手机
adb push ~/Desktop/perfetto.pbtx /data/local/tmp/perfetto.pbtx

# 2. 开始抓取
adb shell 'cat /data/local/tmp/perfetto.pbtx | perfetto --txt -c - -o /data/misc/perfetto-traces/trace'

# 3. 结束抓取
adb shell 'perfetto --attach=perf_debug --stop'
```

### 3.3 Perfetto UI 抓取

1. 选择 ADB 连接的设备
2. 在 Perfetto UI 配置并点击【Start Recording】
3. 等待 Max Duration 倒计时结束
4. 自动在 Web 界面打开 Trace

**缺点：** 不能下载 Trace 文件分享给他人

### 3.4 Python 脚本抓取（推荐）

```bash
# 下载脚本
curl -O https://raw.githubusercontent.com/google/perfetto/master/tools/record_android_trace

# 运行抓取
python3 record_android_trace -c perfetto.pbtx -o trace_file.perfetto-trace

# 操作 App 后按 Ctrl+C 结束
```

**优点：** 自动下载 trace_processor，自动在浏览器打开

---

## 四、Trace 分析

### 4.1 代码标记 Trace

```java
// 在代码中标记 Trace 段
Trace.beginSection("Choreographer#doFrame");
// ... 要分析的代码 ...
Trace.endSection();
```

### 4.2 基本操作

1. **观察线程**：整体查看耗时久、Uninterruptible Sleep 的线程
2. **钉住线程**：点击钉图标将目标线程钉在顶部，方便对比

### 4.3 常见性能问题

#### 4.3.1 Uninterruptible Sleep (non-IO)

**现象：** Trace 段耗时异常长

**定位方法：**
1. 选中异常段，查看 Duration 列表
2. 放大横轴，找到 Runnable 和 Running
3. 选中最近的 Runnable，查看 Waker 信息
4. Waker 显示唤起当前线程的调用方

#### 4.3.2 Monitor Contention

**现象：** `monitor contention with owner [xxx]`

**表现：** 阻塞主线程或渲染线程

**定位：** 选中 Runnable 查看 Waker 是哪个线程

#### 4.3.3 Lock Contention

**现象：** `Lock contention on InternTable lock`

**常见场景：** App 启动或页面操作时

---

## 五、SQL 聚合分析

### 5.1 常用查询

```sql
-- 统计特定 Trace 平均耗时
SELECT name, AVG(dur)/1000 AS dur
FROM slice
WHERE name = 'renderConvertView[smart_ui_jiangliu]'
GROUP BY name

-- 按耗时降序排序
SELECT ts, dur, name
FROM slice
WHERE name = 'read from memory'
ORDER BY dur DESC
```

### 5.2 相关文档

- [常见查询](https://perfetto.dev/docs/analysis/common-queries)
- [SQL 语法](https://perfetto.dev/docs/analysis/perfetto-sql-syntax)
- [表字段](https://perfetto.dev/docs/analysis/sql-tables)

---

## 六、总结

| 步骤 | 工具/方式 | 说明 |
|------|-----------|------|
| 配置生成 | Perfetto UI | 可视化配置 |
| 抓取 | Python 脚本（推荐） | 自动打开 UI |
| 分析 | Perfetto UI | 图形界面 + SQL |

**Trace 分析要点：**
1. 观察整体线程状态，找异常段
2. 钉住相关线程（主线程、渲染线程）
3. 通过 Runnable 的 Waker 定位阻塞来源
4. 使用 SQL 做聚合分析
