---
source: 远端仓库 despicablemme/KnowledgeDatabase (本地重新整理)
title: "Android Camera2 API 开发笔记"
collected_at: 2026-06-06
tags: [Android, Camera2, CameraX, 相机开发]
references:
  - 远端原始文件: Camera2Demo.md
  - CameraX开发笔记: CameraX开发笔记.md
---

# Android Camera2 API 开发笔记

> 来源：远端知识库重新整理 | 整理时间：2026-06-06

---

## 一、Camera2 核心流程

### 1.1 获取 Camera Device

从 CameraManager 获取 camera device：

```java
// 1. 获取 CameraManager
CameraManager cameraManager = (CameraManager) context.getSystemService(Context.CAMERA_SERVICE);

// 2. 打开相机，传入 stateCallback
cameraManager.openCamera(cameraId, cameraDeviceStateCallback, handler);
```

### 1.2 CameraDevice.StateCallback

在 StateCallback 中实现 `onOpened` 回调：

```java
private final CameraDevice.StateCallback stateCallback = new CameraDevice.StateCallback() {
    @Override
    public void onOpened(@NonNull CameraDevice camera) {
        // onOpened 中创建 CaptureSession
        createCaptureSession(camera, previewSurface);
    }

    @Override
    public void onDisconnected(@NonNull CameraDevice camera) {
        camera.close();
    }

    @Override
    public void onError(@NonNull CameraDevice camera, int error) {
        camera.close();
    }
};
```

---

## 二、创建 CameraCaptureSession

### 2.1 Session 创建流程

```java
private void createCaptureSession(CameraDevice camera, Surface previewSurface) {
    // 1. 创建 Surface（通常用 ImageReader 获取原始数据）
    ImageReader imageReader = ImageReader.newInstance(width, height, ImageFormat.JPEG, 2);
    Surface imageSurface = imageReader.getSurface();

    // 2. 创建 CaptureSession
    List<Surface> surfaces = Arrays.asList(previewSurface, imageSurface);
    
    camera.createCaptureSession(surfaces, new CameraCaptureSession.StateCallback() {
        @Override
        public void onConfigured(@NonNull CameraCaptureSession session) {
            // 3. 在 onConfigured 中构建 CaptureRequest
            buildCaptureRequest(session, previewSurface);
        }

        @Override
        public void onConfigureFailed(@NonNull CameraCaptureSession session) {
            // 配置失败处理
        }
    }, handler);
}
```

### 2.2 重复获取预览流

```java
private void buildCaptureRequest(CameraCaptureSession session, Surface previewSurface) {
    try {
        // 创建 CaptureRequest
        CaptureRequest.Builder builder = session.getDevice().createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);
        builder.addTarget(previewSurface);

        // 设置自动对焦、自动曝光
        builder.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE);
        builder.set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON_AUTO_FLASH);

        // 重复获取预览流
        session.setRepeatingRequest(builder.build(), null, handler);

    } catch (CameraAccessException e) {
        e.printStackTrace();
    }
}
```

---

## 三、ImageReader 获取原始数据

ImageReader 用于从预览流中获取原始图像数据：

```java
// 创建 ImageReader
ImageReader imageReader = ImageReader.newInstance(
    previewSize.getWidth(),
    previewSize.getHeight(),
    ImageFormat.JPEG,
    2  // maxImages: 同时持有的最大图像数
);

// 设置可用的图像监听器
imageReader.setOnImageAvailableListener(new ImageReader.OnImageAvailableListener() {
    @Override
    public void onImageAvailable(ImageReader reader) {
        // 获取最新图像
        Image image = reader.acquireLatestImage();
        if (image != null) {
            // 处理图像数据
            ByteBuffer buffer = image.getPlanes()[0].getBuffer();
            byte[] data = new byte[buffer.remaining()];
            buffer.get(data);
            
            // 处理完成后关闭
            image.close();
        }
    }
}, handler);
```

### 常见问题：添加 ImageReader 后预览停止

**原因**：Surface 被 ImageReader 占用后未正确释放  
**解决**：确保 ImageReader 和 Preview 使用独立的 Surface，且在不需要时及时调用 `close()`

---

## 四、Camera2 vs CameraX 对比

| 特性 | Camera2 | CameraX |
|------|---------|---------|
| 封装程度 | 底层 API | 高级封装 |
| 代码量 | 较多 | 简洁 |
| 生命周期管理 | 手动 | 自动（绑定到 LifecycleOwner） |
| 兼容性 | API 21+，部分功能需 28+ | API 21+ 自动适配 |
| 适用场景 | 需要精细控制 | 快速开发 |

**CameraX 是在 Camera2 基础上实现的高级 API**，推荐优先使用 CameraX，复杂场景再用 Camera2。

---

## 五、屏幕旋转与图像方向

三个要素：
1. **屏幕旋转角度**（逆时针）
2. **相机物理角度**（需要顺时针旋转多少度才能摆正）
3. **图像旋转角度**（需要顺时针旋转的角度）

> 参考：[Google 官方文档：图像旋转角度与相机物理角度](https://developer.android.com/media/camera/camerax/orientation-rotation?hl=zh-cn)

---

## 六、常见问题记录

| 问题 | 可能原因 |
|------|---------|
| 预览黑屏 | Surface 未正确绑定、CameraDevice 未打开 |
| 添加 ImageReader 后预览停止 | Surface 冲突、ImageReader 未正确释放 |
| 拍摄照片模糊 | 未等待对焦完成、相机抖动 |
| 前置摄像头镜像 | 正常现象，需手动处理 Matrix 翻转 |
