# Android Path 常用方法解析

> 原文链接1：https://cloud.tencent.com/developer/article/1179339
> 原文链接2：https://www.cnblogs.com/coding-way/p/3595653.html
> 作者：Anlia（简书）

---

## 一、xxxTo 方法

Path 类中提供了一套 xxxTo 方法，其作用是从起点到终点移动 path 画笔并绘制线（moveTo 方法只移动 path 画笔不绘制线），线有直线和曲线。

### 方法汇总

| 方法 | 说明 |
|------|------|
| lineTo(float x, float y) | 绘制直线，x：终点x坐标值，y：终点y坐标值 |
| moveTo(float x, float y) | 移动画笔，x：终点x坐标值，y：终点y坐标值 |
| arcTo(RectF oval, float startAngle, float sweepAngle) | 绘制圆弧，oval：圆弧矩形区域，startAngle：起始角度，sweepAngle：圆弧旋转的角度 |
| arcTo(RectF oval, float startAngle, float sweepAngle, boolean forceMoveTo) | 绘制圆弧，forceMoveTo：是否在绘制圆弧前移动（moveTo）path画笔位置 |
| arcTo(float left, float top, float right, float bottom, float startAngle, float sweepAngle, boolean forceMoveTo) | 绘制圆弧，left、top、right、bottom组成圆弧矩形区域 |
| quadTo(float x1, float y1, float x2, float y2) | 绘制二阶贝塞尔曲线，控制点坐标：(x1,y1)，终点坐标：(x2,y2) |
| cubicTo(float x1, float y1, float x2, float y2, float x3, float y3) | 绘制三阶贝塞尔曲线，控制点1坐标为(x1,y1)，控制点2坐标为(x2,y2)，终点坐标为(x3,y3) |

### 1. lineTo(float x, float y)

绘制直线，从当前画笔位置出发，连接终点(x,y)。

```java
path.lineTo(300,300);
canvas.drawPath(path,paint);
```

### 2. moveTo(float x, float y)

移动画笔，从当前画笔位置移动到终点(x,y)，不绘制线。

```java
path.moveTo(100,100);
path.lineTo(300,300);
canvas.drawPath(path,paint);
```

### 3. arcTo

#### arcTo(RectF oval, float startAngle, float sweepAngle)

绘制圆弧，从当前画笔位置出发，连线到内切矩形区域 oval 的圆弧的起始角度 startAngle 位置（X轴正方向为0°），顺时针旋转绘制圆弧，旋转度数为 sweepAngle（sweepAngle为负时则逆时针旋转）。

```java
RectF rectF = new RectF(100,100,300,400);
path.arcTo(rectF,0,180);
canvas.drawPath(path,pathPaint);
```

#### arcTo(RectF oval, float startAngle, float sweepAngle, boolean forceMoveTo)

若 forceMoveTo 为 false，则用法和 arcTo(RectF oval, float startAngle, float sweepAngle) 一样，绘制圆弧之前不会移动（moveTo）path 画笔位置。若为 true，先强制调用 moveTo 移动 path 画笔至圆弧起点，再绘制圆弧。

注意：如果调用 arcTo 方法之前没有对 path 进行任何操作，则 forceMoveTo 设置 true 或 false 效果都一样。

```java
// forceMoveTo = false
RectF rectF = new RectF(100,100,300,400);
path.moveTo(100,100);
path.arcTo(rectF,0,180,false);
path.close();
canvas.drawPath(path,pathPaint);

// forceMoveTo = true
RectF rectF = new RectF(100,100,300,400);
path.moveTo(100,100);
path.arcTo(rectF,0,180,true);
path.close();
canvas.drawPath(path,pathPaint);
```

#### arcTo(float left, float top, float right, float bottom, float startAngle, float sweepAngle, boolean forceMoveTo)

与 arcTo(RectF oval, float startAngle, float sweepAngle, boolean forceMoveTo) 用法一样。

### 4. quadTo(float x1, float y1, float x2, float y2)

从 path 画笔当前位置出发，以(x₁,y₁)为控制点，向终点(x₂,y₂)绘制一条二阶贝塞尔曲线。

```java
path.moveTo(100,100);
path.quadTo(200,0,400,100);
canvas.drawPath(path,pathPaint);
```

### 5. cubicTo(float x1, float y1, float x2, float y2, float x3, float y3)

从 path 画笔当前位置出发，以(x1,y1)为控制点1，以(x2,y2)为控制点2，向终点(x3,y3)绘制一条三阶贝塞尔曲线。

```java
path.moveTo(100,100);
path.cubicTo(200,0,300,90,500,100);
canvas.drawPath(path,pathPaint);
```

圆形也是由四段三阶贝塞尔曲线组成：

```java
path.moveTo(300,200);
path.cubicTo(300,200+100*0.551915024494f,200+100*0.551915024494f,300,200,300);

path.moveTo(200-20,300);
path.cubicTo(200-100*0.551915024494f-20,300,100-20,200+100*0.551915024494f,100-20,200);
canvas.drawPath(path,pathPaint);
```

---

## 二、rXxxTo 方法

rXxxTo 方法的 r 意思是 relative（相对），其功能与对应的 xxxTo 方法一样，区别在于 rXxxTo 方法在绘制 Path 时是以当前 path 画笔位置为坐标原点，即相对于 path 画笔位置进行绘制，而 xxxTo 方法的坐标原点则与当前 canvas 坐标原点一致。

例如，使用 xxxTo 方法：
```java
path.moveTo(100,100);
path.lineTo(300,300);
canvas.drawPath(path, pathPaint);
```
上述代码是从 (100,100) 到 (300,300) 绘制一条直线。

那么如果用 rXxxTo 方法，相对 (100,100) 这个点绘制直线，则终点应为 (300-100,300-100)，即终点设为 (200,200)：
```java
path.moveTo(100,100);
path.rLineTo(200,200);
canvas.drawPath(path, pathPaint);
```

效果是一样的。

---

## 三、addXxx 方法

Path 类中还提供了一套 addXxx 方法，字面理解就是添加一段相应的线，线可以是曲线、完整的圆形、矩形等，甚至可以是另一组 Path 的线。所谓添加的意思，就是在绘制这段线前，移动（moveTo）path 画笔位置到线的起始位置，然后再绘制线，也就是说添加的这段线，与之前绘制的 Path 是分离的（除非后绘制的这段线的起始点与之前 Path 的终点一致）。

### 方法汇总

| 方法 | 说明 |
|------|------|
| addArc(RectF oval, float startAngle, float sweepAngle) | 添加圆弧，oval：圆弧矩形区域，startAngle：起始角度，sweepAngle：圆弧旋转的角度 |
| addArc(float left, float top, float right, float bottom, float startAngle, float sweepAngle) | 添加圆弧（API 19以上有效） |
| addCircle(float x, float y, float radius, Direction dir) | 添加圆形，x/y：圆心坐标，radius：半径，dir：线的闭合方向（CW顺时针 \| CCW逆时针） |
| addOval(RectF oval, Direction dir) | 添加椭圆，oval：椭圆内切的矩形区域 |
| addOval(float left, float top, float right, float bottom, Direction dir) | 添加椭圆 |
| addRect(RectF rect, Direction dir) | 添加矩形，rect：矩形区域 |
| addRect(float left, float top, float right, float bottom, Direction dir) | 添加矩形 |
| addRoundRect(RectF rect, float rx, float ry, Direction dir) | 添加统一圆角的圆角矩形 |
| addRoundRect(float left, float top, float right, float bottom, float rx, float ry, Direction dir) | 添加统一圆角的圆角矩形 |
| addRoundRect(RectF rect, float[] radii, Direction dir) | 添加非统一圆角的圆角矩形，radii：矩形四个椭圆圆角的横轴半径和纵轴半径的数组，一共8个数值 |
| addRoundRect(float left, float top, float right, float bottom, float[] radii, Direction dir) | 添加非统一圆角的圆角矩形 |
| addPath(Path src) | 添加一组Path |
| addPath(Path src, float dx, float dy) | 添加一组平移后的Path |
| addPath(Path src, Matrix matrix) | 添加一组经过矩阵变换后的Path |

### 1. addArc

addArc 两个方法使用起来与 arcTo 中 forceMoveTo 设置为 true 效果一致。

### 2. addCircle(float x, float y, float radius, Direction dir)

以点 (x,y) 为圆心，添加一个半径长为 radius 的圆形，绘制起始角度为0°（x轴方向），绘制方向通过 dir 的值而定，dir 为 CW 时顺时针绘制，dir 为 CCW 时逆时针绘制。

```java
// 顺时针
path.addCircle(200,150,100, Path.Direction.CW);
canvas.drawPath(path,pathPaint);
canvas.drawTextOnPath("绘制顺序", path, 0, 0, paint);

// 逆时针
path.addCircle(200,150,100, Path.Direction.CCW);
canvas.drawPath(path,pathPaint);
canvas.drawTextOnPath("绘制顺序", path, 0, 0, paint);
```

### 3. addOval

在 oval 矩形区域中，添加一个内切的椭圆，绘制起始角度为0°（x轴方向），绘制方向通过 dir 的值而定。

```java
RectF rectF = new RectF(100,100,400,250);
path.addOval(rectF, Path.Direction.CW);
canvas.drawPath(path,pathPaint);
```

### 4. addRect

添加一个区域为 rect 的矩形，绘制起点为左上角，绘制方向通过 dir 的值而定。

```java
RectF rectF = new RectF(100,100,400,250);
path.addRect(rectF, Path.Direction.CW);
canvas.drawPath(path,pathPaint);
canvas.drawTextOnPath("绘制顺序", path, 0, 0, paint);
```

### 5. addRoundRect

添加一个区域为 rect 的圆角矩形，四个角的圆角大小一致，圆角的横轴半径为 rx，纵轴半径为 ry。dir 为 CW 时顺时针绘制，绘制起点为左下角；dir 为 CCW 时逆时针绘制，绘制起点为左上角。

```java
RectF rectF = new RectF(100,100,400,350);
path.addRoundRect(rectF,60,30,Path.Direction.CW);
canvas.drawPath(path,pathPaint);
canvas.drawTextOnPath("绘制顺序", path, 0, 0, paint);

RectF rectF = new RectF(100,100,400,350);
path.addRoundRect(rectF,60,30,Path.Direction.CCW);
canvas.drawPath(path,pathPaint);
canvas.drawTextOnPath("绘制顺序", path, 0, 0, paint);
```

对于非统一圆角，使用 radii 数组指定四个角的圆角半径（需要8个数值）：

```java
RectF rectF = new RectF(100,100,400,350);
float[] radii = {60,30,30,70,100,100,10,40};
path.addRoundRect(rectF,radii,Path.Direction.CW);
canvas.drawPath(path,pathPaint);
canvas.drawTextOnPath("绘制顺序", path, 0, 0, paint);
```

注意：如果 radii 数组中的元素小于8，系统会抛出错误信息 "radii[] needs 8 values"。

### 6. addPath

#### addPath(Path src)

添加一组名为 src 的 Path 副本。

```java
Path copyPath = new Path();
copyPath.moveTo(100,100);
copyPath.lineTo(150,200);
copyPath.quadTo(200,100,350,200);
copyPath.lineTo(100,250);
copyPath.close();
path.addPath(copyPath);
canvas.drawPath(path,pathPaint);
```

#### addPath(Path src, float dx, float dy)

添加一组名为 src 的 Path 副本，然后将其进行平移，x 轴上的平移距离为 dx，y 轴上的平移距离为 dy。

```java
path.addPath(copyPath,300,0);
```

#### addPath(Path src, Matrix matrix)

添加一组名为 src 的 Path 副本，然后将其进行矩阵变换。

```java
Matrix mMatrix = new Matrix();
mMatrix.setScale(1,-1);
mMatrix.postRotate(90);
path.addPath(copyPath,mMatrix);
canvas.drawPath(path,pathPaint);
```

---

## 四、填充模式 (FillType)

### 方法汇总

| 方法 | 说明 |
|------|------|
| setFillType(FillType ft) | 设置Path的填充模式，有EVEN_ODD、INVERSE_EVEN_ODD、WINDING、INVERSE_WINDING四种模式 |
| getFillType() | 获取当前Path的填充模式 |
| isInverseFillType() | 判断当前Path填充模式是否是反向规则(INVERSE_XXX) |
| toggleInverseFillType() | 当前Path的填充模式与其反向规则模式进行相互切换 |

### 填充模式详解

对于简单的封闭图形（路径无相交的现象），图形的外部和内部很容易判断。但如果路径有相交的情况，对应重叠的部分，使用不同的填充模式，内部和外部的定义有所不同。

#### EVEN_ODD（奇偶规则）

意味着如果用一条直线横贯图形时，外部和内部交替出现。

#### WINDING（非零环绕规则）

对应一条曲线 C 和指定点 P，创建一条由 P 出发的任意方向无限延伸的直线。找到曲线 C 和这条直线的所有交点。计算所有由顺时针方向和曲线相交的交点的个数，再计算由逆时针方向和曲线相交的个数，如果两个数相等，表示这个点在曲线内部，如果不等，表示这个点在曲线外部。

#### INVERSE_EVEN_ODD 和 INVERSE_WINDING

是上述两种模式的反模式。

### 四种模式示例

```java
showPath(canvas, 0, 0, Path.FillType.WINDING, paint);
showPath(canvas, 160, 0, Path.FillType.EVEN_ODD, paint);
showPath(canvas, 0, 160, Path.FillType.INVERSE_WINDING, paint);
showPath(canvas, 160, 160, Path.FillType.INVERSE_EVEN_ODD, paint);
```

---

## 五、其他方法

| 方法 | 说明 |
|------|------|
| close() | 封闭当前Path，连接起点和终点 |
| reset() | 清空Path中的所有直线和曲线，保留填充模式设置，不保留Path上相关的数据结构 |
| rewind() | 清空Path中的所有直线和曲线，不保留填充模式设置，但会保留Path上相关的数据结构，以便高效地复用 |
| set(Path src) | 用名为src的Path替换当前的Path |
| op(Path path, Op op) | 当前Path与名为path的Path进行布尔运算（API 19以上有效） |
| offset(float dx, float dy) | 平移当前Path |
| offset(float dx, float dy, Path dst) | 平移名为dst的Path |
| transform(Matrix matrix) | 对当前Path进行矩阵变换 |
| transform(Matrix matrix, Path dst) | 对名为dst的Path进行矩阵变换 |
| setLastPoint(float dx, float dy) | 设置终点，设置当前Path最后一个点的位置为(dx,dy) |
| isEmpty() | 判断当前Path是否为空 |
| isConvex() | 判断当前Path围成的图形是否凸多边形（API 21以上有效） |
| isRect(RectF rect) | 判断当前Path是否为矩形 |

### 1. op(Path path, Op op) 布尔运算

参数 op 共有五种运算逻辑：

| 运算逻辑 | 说明 |
|----------|------|
| DIFFERENCE（差集） | path1 减去与 path2 的交集后剩下的部分，即 path1 与 path2 的并集减去 path2 部分 |
| REVERSE_DIFFERENCE（差集） | path2 减去与 path1 的交集后剩下的部分，即 path1 与 path2 的并集减去 path1 部分 |
| INTERSECT（交集） | path1 与 path2 的交集 |
| UNION（并集） | path1 与 path2 的并集 |
| XOR（异或） | path1 与 path2 的并集减去 path1 与 path2 的交集 |

示例基本图形：
```java
Path path1 = new Path();
path1.addRect(100,100,300,300, Path.Direction.CW);
pathPaint.setColor(Color.GREEN);
canvas.drawPath(path1,pathPaint);

Path path2 = new Path();
path2.addCircle(300,250,100,Path.Direction.CW);
pathPaint.setColor(Color.RED);
canvas.drawPath(path2,pathPaint);
```

布尔运算示例：
```java
// DIFFERENCE
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
    path1.op(path2, Path.Op.DIFFERENCE);
    canvas.drawPath(path1,pathPaint);
}

// INTERSECT
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
    path1.op(path2, Path.Op.INTERSECT);
    canvas.drawPath(path1,pathPaint);
}

// UNION
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
    path1.op(path2, Path.Op.UNION);
    canvas.drawPath(path1,pathPaint);
}

// XOR
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
    path1.op(path2, Path.Op.XOR);
    canvas.drawPath(path1,pathPaint);
}
```

可以用 path1.op 直接运算，也可以新建一个 path3 保存 path1 和 path2 的运算结果，效果都是一样的。

### 2. setLastPoint(float dx, float dy)

当 Path 在调用 setLastPoint 方法之前执行了某项操作时（绘制直线或曲线等），会将该操作的终点强制设置为 (dx,dy) 并连线（线的曲直取决于该操作本身是绘制直线还是曲线）。

理解这个方法之前，首先要知道无论是使用 addXxx 方法还是 xxxTo 方法等在绘制过程中其实都是根据一堆点的集合，按顺序连线（直线或曲线）后绘制出 Path 最终的样子，setLastPoint 方法正是改变此方法调用之前点的集合中最后一个点的位置。

封闭图形（矩形）示例：
```java
path.addRect(new RectF(100,100,300,300), Path.Direction.CW);
pathPaint.setColor(Color.GREEN);
canvas.drawPath(path,pathPaint);

path.reset();
path.addRect(new RectF(100,100,300,300), Path.Direction.CW);
path.setLastPoint(150,250);
pathPaint.setColor(Color.RED);
canvas.drawPath(path,pathPaint);
```

非封闭图形（圆弧）示例：
```java
path.addArc(new RectF(100,100,300,300),0,180);
pathPaint.setColor(Color.GREEN);
canvas.drawPath(path,pathPaint);

path.reset();
path.addArc(new RectF(100,100,300,300),0,180);
path.setLastPoint(200,200);
pathPaint.setColor(Color.RED);
canvas.drawPath(path,pathPaint);
```

---

## 六、xxxTo 与 addXxx 的区别

- **xxxTo 方法**：从当前画笔位置出发，连接终点绘制线
- **addXxx 方法**：添加一段相应的线，在绘制这段线前会自动移动（moveTo）path 画笔位置到线的起始位置，添加的这段线与之前绘制的 Path 是分离的

---
添加时间：2026-04-28 22:16:36
