---
source: 远端仓库 despicablemme/KnowledgeDatabase (本地重新整理)
title: "Android UI 组件笔记"
collected_at: 2026-06-06
tags: [Android, UI, Button, SurfaceView, ListView, GridView]
references:
  - 远端原始文件: UI.md
---

# Android UI 组件笔记

> 来源：远端知识库重新整理 | 整理时间：2026-06-06

---

## 一、Button 样式问题

### 1.1 Button 颜色无法修改（总是紫色）

**原因**：Theme 使用了 MaterialComponents 但未启用 Bridge 模式

**解决**：在 `res/values/themes.xml` 和 `res/values-night/themes.xml` 中修改：

```xml
<!-- 修改前 -->
<style name="Theme.MyApplication" parent="Theme.MaterialComponents.DayNight.DarkActionBar">

<!-- 修改后 -->
<style name="Theme.MyApplication" parent="Theme.MaterialComponents.DayNight.DarkActionBar.Bridge">
```

添加 `.Bridge` 后可以让自定义主题正确继承 MaterialComponents 样式。

---

## 二、Button 背景颜色与按下效果

在 `res/drawable/` 目录下创建 `button_selector.xml`：

```xml
<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- 按下状态 -->
    <item android:state_pressed="true">
        <shape>
            <solid android:color="@android:color/holo_red_light"/>
            <stroke android:width="1dp" android:color="@color/material_dynamic_neutral80"/>
            <corners android:radius="100dp"/>
        </shape>
    </item>

    <!-- 禁用状态 -->
    <item android:state_enabled="false">
        <shape>
            <solid android:color="@color/material_dynamic_neutral80"/>
            <stroke android:width="1dp" android:color="@color/material_dynamic_neutral80"/>
            <corners android:radius="100dp"/>
        </shape>
    </item>

    <!-- 默认状态 -->
    <item>
        <shape>
            <solid android:color="@android:color/white"/>
            <stroke android:width="1dp" android:color="@color/material_dynamic_neutral80"/>
            <corners android:radius="100dp"/>
        </shape>
    </item>

</selector>
```

**使用方式**：

```xml
<Button
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:background="@drawable/button_selector"/>
```

---

## 三、SurfaceView

`SurfaceView` 继承自 View，可通过代码动态改变大小。

### 3.1 常用方法

```java
// 获取 Holder
Holder holder = getSurfaceHolder();

// 从 Layout 获取尺寸
holder.setSizeFromLayout();

// 设置固定尺寸
holder.setFixedSize(width, height);
```

### 3.2 SurfaceView 使用场景

- 视频播放
- 相机预览
- 游戏开发
- 需要频繁更新的自定义视图

---

## 四、ListView

ListView 用于显示垂直滚动列表。

### 4.1 开发步骤

1. 在布局中添加 ListView
2. 为每个 Item 创建单独的布局文件
3. 创建并配置 Adapter
4. 调用 `listView.setAdapter(adapter)`

### 4.2 ArrayAdapter（简单列表）

```kotlin
val list = listOf("Apple", "Banana", "Orange")
val adapter = ArrayAdapter(
    this,
    android.R.layout.simple_list_item_1,  // 内置布局
    list
)
listView.adapter = adapter
```

### 4.3 SimpleAdapter（复杂列表）

```kotlin
val dataList = listOf(
    mapOf("name" to "Alice", "age" to "20"),
    mapOf("name" to "Bob", "age" to "21")
)

val adapter = SimpleAdapter(
    context,
    dataList,                    // List<Map<String, Object>>
    R.layout.list_item_layout,   // Item 布局
    arrayOf("name", "age"),      // 数据 key
    intArrayOf(R.id.nameText, R.id.ageText)  // 对应控件 ID
)

listView.adapter = adapter
```

### 4.4 BaseAdapter（完全自定义）

```kotlin
class MyAdapter(private val data: List<Item>) : BaseAdapter() {
    override fun getCount() = data.size
    override fun getItem(position: Int) = data[position]
    override fun getItemId(position: Int) = position.toLong()
    
    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        // 自定义 Item 布局
        val view = convertView ?: LayoutInflater.from(parent.context)
            .inflate(R.layout.list_item, parent, false)
        // 绑定数据...
        return view
    }
}
```

### 4.5 setViewBinder 灵活显示

```kotlin
adapter.setViewBinder { view, data, textRepresentation ->
    when (view.id) {
        R.id.customView -> {
            // 自定义显示逻辑
            true  // 返回 true 表示已处理
        }
        else -> false  // 返回 false 使用默认逻辑
    }
}
```

---

## 五、GridView

GridView 用于显示网格布局的列表。

### 5.1 基本用法

```xml
<GridView
    android:id="@+id/gridView"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:numColumns="3"
    android:horizontalSpacing="10dp"
    android:verticalSpacing="10dp"/>
```

### 5.2 配合 Adapter 使用

与 ListView 类似，使用 `setAdapter()` 设置数据源。

---

## 六、RecyclerView（推荐替代 ListView/GridView）

`RecyclerView` 是 ListView 和 GridView 的现代替代品，性能更好。

```kotlin
// 创建 Adapter
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {
    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView)
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        // 绑定数据
    }
    
    override fun getItemCount() = data.size
}

// 设置 LayoutManager 和 Adapter
recyclerView.layoutManager = LinearLayoutManager(this)
recyclerView.adapter = MyAdapter()
```

---

## 七、常见问题

| 问题 | 解决方案 |
|------|---------|
| Button 样式不生效 | 检查是否正确引用 drawable selector |
| ListView Item 点击无响应 | 设置 `listView.setOnItemClickListener()` |
| GridView 列数不对 | 检查 `android:numColumns` 设置 |
| RecyclerView 性能差 | 使用 ViewHolder 模式，避免在 onBindViewHolder 中创建对象 |
