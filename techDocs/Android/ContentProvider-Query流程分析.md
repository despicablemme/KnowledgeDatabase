---
source: https://blog.csdn.net/vviccc/article/details/143694653
title: "Android Framework AMS（15）ContentProvider分析-2(getContentResolver及ContentResolver.query流程解读)"
collected_at: 2026-03-21
tags: [Android, Framework, ContentProvider, AMS, 源码分析]
references:
  - https://blog.csdn.net/vviccc/article/details/143694653
  - 专题总纲: https://blog.csdn.net/vviccc/article/details/103477944
---

# ContentProvider 流程分析：getContentResolver 及 query

> 来源：CSDN | 作者：vviccc

---

## 一、getContentResolver 流程

### 关键代码

```java
// Context（抽象方法）
public abstract ContentResolver getContentResolver();

// ContextImpl（真正实现）
private final ApplicationContentResolver mContentResolver;

@Override
public ContentResolver getContentResolver() {
    return mContentResolver;
}
```

### ApplicationContentResolver 内部类

```java
private static final class ApplicationContentResolver extends ContentResolver {
    private final ActivityThread mMainThread;      // 主线程引用
    private final UserHandle mUser;               // 用户标识

    // 获取稳定的 ContentProvider 连接
    @Override
    protected IContentProvider acquireProvider(Context context, String auth) {
        return mMainThread.acquireProvider(context,
            ContentProvider.getAuthorityWithoutUserId(auth),
            resolveUserIdFromAuthority(auth), true);
    }

    // 获取不稳定的 ContentProvider 连接
    @Override
    protected IContentProvider acquireUnstableProvider(Context c, String auth) {
        return mMainThread.acquireProvider(c,
            ContentProvider.getAuthorityWithoutUserId(auth),
            resolveUserIdFromAuthority(auth), false);  // false = unstable
    }
}
```

---

## 二、ContentResolver.query 流程

### 核心流程图

```
ContentResolver.query()
    ↓
acquireUnstableProvider(uri)  ← 获取不稳定的 Provider
    ↓
unstableProvider.query()       ← 尝试查询
    ↓ (如果 DeadObjectException)
acquireProvider(uri)           ← 获取稳定的 Provider 重试
    ↓
返回 CursorWrapperInner        ← 包装 Cursor 返回
```

### 关键代码分析

```java
public final Cursor query(final Uri uri, String[] projection,
        String selection, String[] selectionArgs, String sortOrder,
        CancellationSignal cancellationSignal) {

    // Step 1: 获取不稳定的 ContentProvider
    IContentProvider unstableProvider = acquireUnstableProvider(uri);
    if (unstableProvider == null) return null;

    IContentProvider stableProvider = null;
    Cursor qCursor = null;

    try {
        // Step 2: 尝试查询
        qCursor = unstableProvider.query(mPackageName, uri, projection,
            selection, selectionArgs, sortOrder, remoteCancellationSignal);

    } catch (DeadObjectException e) {
        // 如果 Provider 死亡，获取稳定的 Provider 重试
        unstableProviderDied(unstableProvider);
        stableProvider = acquireProvider(uri);
        if (stableProvider == null) return null;
        qCursor = stableProvider.query(...);
    }

    // Step 3: 返回包装后的 Cursor
    CursorWrapperInner wrapper = new CursorWrapperInner(qCursor,
        stableProvider != null ? stableProvider : acquireProvider(uri));
    return wrapper;

} finally {
    // Step 4: 释放资源
    if (qCursor != null) qCursor.close();
    if (unstableProvider != null) releaseUnstableProvider(unstableProvider);
    if (stableProvider != null) releaseProvider(stableProvider);
}
```

---

## 三、为什么需要 Unstable Provider？

| 对比项 | Unstable Provider | Stable Provider |
|--------|-------------------|------------------|
| 获取速度 | 快 | 慢 |
| 资源占用 | 低 | 高 |
| 状态检查 | 无 | 有额外同步 |
| 使用场景 | Provider 健康时 | Provider 崩溃后备 |

**设计原因：**
1. **性能优化**：不稳定连接更快，减少查询延迟
2. **资源管理**：避免频繁建立稳定连接造成的资源浪费
3. **容错机制**：Provider 崩溃时自动切换到稳定连接

---

## 四、acquireProvider 流程（ActivityThread）

```java
public final IContentProvider acquireProvider(
        Context c, String auth, int userId, boolean stable) {

    // 1. 尝试获取已存在的 Provider
    final IContentProvider provider = acquireExistingProvider(c, auth, userId, stable);
    if (provider != null) return provider;

    // 2. 向 AMS 获取 ContentProviderHolder
    IActivityManager.ContentProviderHolder holder = null;
    holder = ActivityManagerNative.getDefault().getContentProvider(
        getApplicationThread(), auth, userId, stable);

    // 3. 安装 Provider
    holder = installProvider(c, holder, holder.info,
        true /*noisy*/, holder.noReleaseNeeded, stable);

    return holder.provider;
}
```

### 4.1 acquireExistingProvider

```java
public final IContentProvider acquireExistingProvider(
        Context c, String auth, int userId, boolean stable) {

    synchronized(mProviderMap) {
        final ProviderKey key = new ProviderKey(auth, userId);
        final ProviderClientRecord pr = mProviderMap.get(key);

        if (pr == null) return null;

        IContentProvider provider = pr.mProvider;
        IBinder jBinder = provider.asBinder();

        // 检查 Binder 是否存活
        if (!jBinder.isBinderAlive()) {
            handleUnstableProviderDiedLocked(jBinder, true);
            return null;
        }

        // 增加引用计数
        ProviderRefCount prc = mProviderRefCountMap.get(jBinder);
        if (prc != null) {
            incProviderRefLocked(prc, stable);
        }

        return provider;
    }
}
```

---

## 五、AMS.getContentProvider

```java
public final ContentProviderHolder getContentProvider(
        IApplicationThread caller, String name, int userId, boolean stable) {

    enforceNotIsolatedCaller("getContentProvider");
    return getContentProviderImpl(caller, name, null, stable, userId);
}

private final ContentProviderHolder getContentProviderImpl(
        IApplicationThread caller, String name, IBinder token,
        boolean stable, int userId) {

    // 1. 检查是否已存在
    cpr = mProviderMap.getProviderByName(name, userId);

    // 2. 如果调用者可以在当前进程运行，直接返回
    if (r != null && cpr.canRunHere(r)) {
        return cpr.newHolder(null);  // provider = null 表示同进程
    }

    // 3. 如果不存在，解析并创建 ContentProviderRecord
    if (!providerRunning) {
        cpi = AppGlobals.getPackageManager().resolveContentProvider(name, ...);
        cpr = new ContentProviderRecord(this, cpi, ai, comp, singleton);
    }

    // 4. 启动或返回已启动的 Provider
    ...
}
```

---

## 六、总结

| 流程 | 关键类 | 作用 |
|------|--------|------|
| getContentResolver | ContextImpl | 返回 ApplicationContentResolver |
| query | ContentResolver | 尝试不稳定→稳定 Provider |
| acquireProvider | ActivityThread | 从缓存或 AMS 获取 Provider |
| acquireExistingProvider | ActivityThread | 从 mProviderMap 查找缓存 |
| getContentProviderImpl | AMS | 启动/返回 ContentProvider |

**核心设计思想：**
- 先用不稳定的 Provider 尝试（快）
- 失败后切换到稳定的 Provider（可靠）
- 通过 mProviderMap 缓存避免重复创建

---

## 附：ContentResolver.query 补充（远端知识库整理）

> 以下内容来自远端知识库，与上方 Framework 源码分析互补

### ContentResolver query 方法参数

```kotlin
val cursor = contentResolver.query(
    uri,                    // 数据类型，如 Images.Media.EXTERNAL_CONTENT_URI
    projection,            // 返回的列，如 arrayOf(MediaStore.Images.Media.DATA, MediaStore.Images.Media.DISPLAY_NAME)
    selection,             // 筛选条件，如 "${MediaStore.Images.Media.DISPLAY_NAME} LIKE ?"
    selectionArgs,         // 筛选参数，如 arrayOf("%jpg%")
    sortOrder              // 排序，如 "${MediaStore.Images.Media.DATE_ADDED} DESC"
)
```

### Cursor 遍历方法

```kotlin
cursor?.use {
    // 调整指针
    while (it.moveToNext()) {
        // 获取所有列名
        val columnNames = it.columnNames
        
        // 获取指定列的索引
        val index = it.getColumnIndex(MediaStore.Images.Media.DATA)
        
        // 获取数据
        val path = it.getString(index)
    }
}
```

### Cursor 常用方法

| 方法 | 说明 |
|------|------|
| `moveToNext()` | 移动到下一条 |
| `moveToFirst()` | 移动到第一条 |
| `moveToLast()` | 移动到最后一条 |
| `moveToPosition(position)` | 移动到指定位置 |
| `getColumnIndex(name)` | 获取列的索引 |
| `getString(index)` | 获取字符串值 |
| `getInt(index)` | 获取整数值 |

---

**远端原始文件**：`ContentProvider.md`
**整理时间**：2026-06-06
