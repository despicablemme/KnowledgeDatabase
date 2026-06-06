---
source: 远端仓库 despicablemme/KnowledgeDatabase (本地重新整理)
title: "Android CameraX 与 Activity/Intent 开发笔记"
collected_at: 2026-06-06
tags: [Android, CameraX, Activity, Intent, ViewBinding, Matrix]
references:
  - 远端原始文件: CameraDemo1st.md
---

# Android CameraX 与 Activity/Intent 开发笔记

> 来源：远端知识库重新整理 | 整理时间：2026-06-06

---

## 一、开发流程总览

1. 新建 Manifest 和 Activity，对应页面布局 layout
2. 在 `build.gradle(app)` 中添加所需依赖（如 CameraX），配置 viewBinding
3. Manifest 中注册所需权限，Activity 中代码申请权限
4. 布局中添加所需组件，代码中实现逻辑

---

## 二、ViewBinding 使用

### 2.1 启用 ViewBinding

在 `build.gradle(app)` 的 android 空间中添加：

```kotlin
buildFeatures {
    viewBinding = true
}
```

### 2.2 Activity 中使用

```kotlin
import com.example.myapplication.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 实例化 binding 对象
        binding = ActivityMainBinding.inflate(layoutInflater)
        
        // 得到布局
        val view = binding.root
        setContentView(view)
        
        // 得到对应元素
        val button = binding.closeButton
    }
}
```

**类名命名规则**：`ActivityMainBinding` 由 `activity_` + `main` + `Binding` 组成

---

## 三、CameraX 快速上手

### 3.1 添加依赖

```kotlin
val cameraxVersion = "1.3.4"
implementation("androidx.camera:camera-core:${cameraxVersion}")
implementation("androidx.camera:camera-camera2:${cameraxVersion}")
implementation("androidx.camera:camera-lifecycle:${cameraxVersion}")
implementation("androidx.camera:camera-video:${cameraxVersion}")
implementation("androidx.camera:camera-view:${cameraxVersion}")
implementation("androidx.camera:camera-extensions:${cameraxVersion}")
```

### 3.2 核心类说明

| 类 | 作用 |
|----|------|
| `ProcessCameraProvider` | 获取相机实例，绑定生命周期 |
| `Camera` | 相机类，包含控制和信息 |
| `CameraSelector` | 选择前后置相机 |
| `CameraControl` | 控制相机：变焦、对焦等 |
| `CameraInfo` | 获取相机信息：焦距、倍数等 |
| `PreviewView` | Layout 组件，显示预览 |
| `Preview` | 预览类，连接 PreviewView |

### 3.3 获取相机预览

```kotlin
// 1. 获取 cameraProviderFuture
val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

// 2. get 到 provider 实例
val cameraProvider = cameraProviderFuture.get()

// 3. 创建 cameraSelector（前后置）
val cameraSelector = CameraSelector.Builder()
    .requireLensFacing(CameraSelector.LENS_FACING_FRONT)
    .build()

// 4. 创建 Preview 并连接 SurfaceProvider
val preview = Preview.Builder().build()
preview.setSurfaceProvider(binding.myPreviewView.getSurfaceProvider())

// 5. 绑定生命周期，得到 camera 实例
val camera = cameraProvider.bindToLifecycle(
    this,           // LifecycleOwner
    cameraSelector, // 相机选择器
    preview        // 预览
)
```

### 3.4 相机控制与信息获取

```kotlin
// 获取控制类
val cameraControl = camera.cameraControl

// 获取信息类
val cameraInfo = camera.cameraInfo

// 常用控制：变焦
cameraControl.setZoomRatio(2.0f)

// 常用控制：对焦
val factory = binding.previewView.meteringPointFactory
val point = factory.createPoint(x, y)
val action = FocusMeteringAction.Builder(point).build()
cameraControl.startFocusAndMetering(action)
```

---

## 四、Activity 生命周期

### 4.1 生命周期回调

```
onCreate() → onStart() → onResume() → 运行中
                              ↓
                      onPause() → onStop() → onDestroy()
```

### 4.2 Activity 状态保存（savedInstanceState）

```kotlin
class MainActivity : AppCompatActivity() {
    private var gameState: String? = null
    private lateinit var textView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.main_activity)
        textView = findViewById(R.id.text_view)

        // 恢复状态
        if (savedInstanceState != null) {
            gameState = savedInstanceState.getString(GAME_STATE_KEY)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString(GAME_STATE_KEY, gameState)
        outState.putString(TEXT_VIEW_KEY, textView.text.toString())
    }

    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        textView.text = savedInstanceState.getString(TEXT_VIEW_KEY)
    }
}
```

### 4.3 注意事项

- `onSaveInstanceState()` 不一定每次都调用（按回退键时不会）
- 它在 `onStop()` 之前，可能在 `onPause()` 之前调用
- 只存储瞬时状态，持久化数据应在 `onPause()` 中存数据库

### 4.4 AppCompatActivity

`AppCompatActivity` 向下兼容带有新特性的 Activity 基类，继承自 `FragmentActivity`，多了一个 `AppCompatDelegate`。

---

## 五、Intent 与 Activity 启动

### 5.1 显式 Intent vs 隐式 Intent

| 类型 | 说明 | 示例 |
|------|------|------|
| **显式 Intent** | 直接指定目标组件 | `Intent(this, SecondActivity::class.java)` |
| **隐式 Intent** | 描述动作，让系统匹配 | `Intent(Intent.ACTION_SEND)` |

### 5.2 创建与启动

```kotlin
// 显式 Intent
val intent = Intent(this, SecondActivity::class.java)
intent.putExtra(EXTRA_USER_NAME, "Alice")
startActivity(intent)

// 隐式 Intent
val sendIntent = Intent().apply {
    action = Intent.ACTION_SEND
    putExtra(Intent.EXTRA_TEXT, "Hello")
    type = "text/plain"
}
startActivity(sendIntent)
```

### 5.3 Manifest 配置（隐式 Intent Filter）

```xml
<activity android:name=".ShareActivity" android:exported="false">
    <intent-filter>
        <action android:name="android.intent.action.SEND"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <data android:mimeType="text/plain"/>
    </intent-filter>
</activity>
```

### 5.4 PendingIntent

`PendingIntent` 是待执行的 Intent，常用于通知、系统权限等场景：

```kotlin
val pendingIntent = PendingIntent.getActivity(
    context,
    0,
    Intent(context, TargetActivity::class.java),
    PendingIntent.FLAG_UPDATE_CURRENT
)
```

---

## 六、Matrix 图像处理

Matrix 用于图像变换：翻转、缩放、旋转等。

### 6.1 常用方法

```kotlin
val matrix = Matrix()
matrix.setRotate(90f)           // 旋转
matrix.setScale(ratioWidth, ratioHeight)  // 缩放
matrix.postTranslate(dx, dy)    // 平移
```

### 6.2 应用场景

**场景1：创建变换后的 Bitmap**

```kotlin
val rotatedBitmap = Bitmap.createBitmap(
    originalBitmap,
    xBias, yBias,
    outputWidth, outputHeight,
    matrix,
    false
)
```

**场景2：在 Canvas 上绘制**

```kotlin
canvas.drawBitmap(bitmap, matrix, Paint())
```

---

## 七、Future 与 ListenableFuture

`ListenableFuture` 是 Google 提供的异步计算结果包装接口：

```kotlin
// 获取 cameraProvider 的典型用法
val cameraProviderFuture = ProcessCameraProvider.getInstance(context)

cameraProviderFuture.addListener({
    val cameraProvider = cameraProviderFuture.get()
    // 使用 cameraProvider
}, ContextCompat.getMainExecutor(context))
```

---

## 八、CameraSelector 选择器

**常见问题**：为什么不能直接传 0 或 1？

```kotlin
// 错误 ❌
val selector = CameraSelector.Builder()
    .requireLensFacing(0)  // 直接传数字
    .build()

// 正确 ✅
val selector = CameraSelector.Builder()
    .requireLensFacing(CameraSelector.LENS_FACING_BACK)  // 使用常量
    .build()
```

**原因**：使用预定义常量可读性更好，且数值可能因版本变化。

---

## 九、常见问题记录

| 问题 | 答案 |
|------|------|
| 为什么 camera 实例在 onResume 第二次才不是空？ | 生命周期绑定需要首次进入流程才能完成初始化 |
| Activity 权限相关 | 使用 `ActivityCompat.requestPermissions()` 或 `registerForActivityResult()` |
| Context 是什么？ | 上下文环境，提供资源访问和系统服务调用的能力 |
| android:exported=false | 禁止其他应用启动此组件 |
