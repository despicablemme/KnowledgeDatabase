---
source: https://blog.csdn.net/carson_ho/article/details/103342511
title: "Carson带你学Android：该如何正确获取View坐标位置？"
collected_at: 2026-03-21
tags: [Android, View, 坐标, 自定义View]
references:
  - https://blog.csdn.net/carson_ho/article/details/103342511
---

# Android 获取 View 坐标的 6 种方式

> 来源：CSDN | 作者：carson_ho

---

## 一、getLeft()、getTop()、getRight()、getBottom()

### 应用场景
获得 View 相对**父 View** 的坐标

### 使用方法

```java
view.getLeft();   // View左边距（相对于父容器）
view.getTop();    // View顶边距（相对于父容器）
view.getRight();  // View右边距（相对于父容器）
view.getBottom(); // View底边距（相对于父容器）
```

### 示意图

```
父View
┌─────────────────────┐
│  ┌───────────────┐  │
│  │ A (left,top)  │  │
│  │    ┌─────┐    │  │
│  │    │View │ B  │  │
│  │    └─────┘    │  │
│  │          C    │  │
│  │              │D │
│  └───────────────┘  │
└─────────────────────┘

A = (getLeft, getTop)
D = (getRight, getBottom)
```

**注意：** View 的位置是相对于父控件而言的

---

## 二、getX()、getY()、getRawX()、getRawY()

### 应用场景
获得点击事件处**相对点击控件 & 屏幕**的坐标

### 使用方法

```java
// 通过 MotionEvent 获取
MotionEvent event;

event.getX();    // 相对于当前点击控件
event.getY();    // 相对于当前点击控件

event.getRawX();  // 相对于屏幕
event.getRawY();  // 相对于屏幕
```

---

## 三、getLocationInWindow()

### 应用场景
获取控件相对**窗口 Window** 的位置

### 使用方法

```java
int[] location = new int[2];
view.getLocationInWindow(location);

int x = location[0]; // View距离Window左边的距离
int y = location[1]; // View距离Window顶边的距离
```

**注意：** 要在 `onWindowFocusChanged()` 里获取，即等窗口发生变化后

---

## 四、getLocationOnScreen()

### 应用场景
获取控件相对**屏幕**的绝对坐标

### 使用方法

```java
int[] location = new int[2];
view.getLocationOnScreen(location);

int x = location[0]; // View距离屏幕左边的距离
int y = location[1]; // View距离屏幕顶边的距离
```

**注意：** 要在 `view.post(Runnable)` 里获取，即等布局变化后

---

## 五、getGlobalVisibleRect()

### 应用场景
获取 View **可见部分**相对于**屏幕**的坐标

### 使用方法

```java
Rect globalRect = new Rect();
view.getGlobalVisibleRect(globalRect);

globalRect.getLeft();
globalRect.getRight();
globalRect.getTop();
globalRect.getBottom();
```

---

## 六、getLocalVisibleRect()

### 应用场景
获取 View **可见部分**相对于**自身 View 位置左上角**的坐标

### 使用方法

```java
Rect localRect = new Rect();
view.getLocalVisibleRect(localRect);

localRect.getLeft();
localRect.getRight();
localRect.getTop();
localRect.getBottom();
```

---

## 总结对比

| 方法 | 相对参考系 | 适用场景 |
|------|------------|----------|
| `getLeft/Top/Right/Bottom` | 父容器 | 相对布局定位 |
| `getX/Y` | 当前控件 | 点击事件坐标 |
| `getRawX/RawY` | 屏幕 | 需要屏幕绝对坐标 |
| `getLocationInWindow()` | 窗口 | Dialog/PopupWindow |
| `getGlobalVisibleRect()` | 屏幕 | 获取可见区域 |
| `getLocalVisibleRect()` | 自身 | 获取自身可见区域 |
| `getLocationOnScreen()` | 屏幕 | 绝对定位 |
