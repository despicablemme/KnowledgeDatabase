---
source: https://blog.csdn.net/lylddingHFFW/article/details/102930560
title: "Tmp detached view should be removed from RecyclerView before it can be recycled"
collected_at: 2026-03-21
tags: [Android, RecyclerView, Bug, ItemAnimator, 异常解决]
references:
  - https://blog.csdn.net/lylddingHFFW/article/details/102930560
---

# RecyclerView 异常：Tmp detached view should be removed before recycled

> 来源：CSDN | 作者：lylddingHFFW

---

## 异常信息

```
java.lang.IllegalArgumentException: 
Tmp detached view should be removed from RecyclerView before it can be recycled: 
ViewHolder{4a13b78 position=1 id=-1, oldPos=-1, pLpos:-1 tmpDetached no parent}
```

---

## 问题原因

在 Item 执行动画结束时，RecyclerView 尝试回收 ViewHolder，但该 ViewHolder 处于 `tmpDetached`（临时分离）状态，还附着在 RecyclerView 上，导致回收冲突。

**调用链：**
```
ItemAnimator.animateAddImpl() 
  → dispatchAddFinished()
    → onAnimationFinished()
      → removeAnimatingView()
        → recycleViewHolderInternal()
          → 抛出异常（isTmpDetached = true）
```

---

## 解决方案

设置 `ItemAnimator = null` 禁用动画：

```java
recyclerView.setItemAnimator(null);
```

**原理：** 异常发生在 Item 动画执行过程中，禁用动画后就不会触发回收冲突。

---

## 相关 API

```java
// 设置 ItemAnimator（传入 null 则禁用动画）
recyclerView.setItemAnimator(null);

// 源码注释
/**
 * Sets the ItemAnimator that will handle animations.
 * If null, no animations will occur when changes occur to the items.
 */
public void setItemAnimator(ItemAnimator animator)
```

---

## ItemAnimator 触发时机

ItemAnimator 在以下三种情况下触发：

| 方法 | 触发 |
|------|------|
| `notifyItemInserted(position)` | 添加动画 |
| `notifyItemRemoved(position)` | 删除动画 |
| `notifyItemChanged(position)` | 更新动画 |

**注意：** `notifyDataSetChanged()` 不会触发动画，会直接重绘。

---

## 总结

| 项目 | 说明 |
|------|------|
| 异常原因 | ViewHolder 处于 tmpDetached 状态时被回收 |
| 解决方案 | `setItemAnimator(null)` 禁用动画 |
| 适用场景 | 列表数据频繁变化，且难以复现动画冲突时 |
