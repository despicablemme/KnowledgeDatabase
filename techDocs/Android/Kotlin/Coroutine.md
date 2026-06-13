# 关键字

### 作用域构建器

- GlobalScope.launch
	code最顶层构建一个协程作用域（main函数中），实际应用中需要手动管理，类似short lifecycle handle a long lifecycle obj, so always useless；
- runBlocking
	- start a coroutine that will block the thread, low efficiency, barely used；
- .launch
	- 在构建器后面点式启动，启动一个对应协程，在协程作用域内直接launch；
	- 启动一个子协程；
- coroutineScope
	- 是一个挂起函数；
	- 主要用来在其他挂起函数中调用并继承外部协程的作用域，因为挂起函数并没有体现调用它的地方的作用域；
	- 其作用域内执行完前，会挂起父协程；
- .async
	- 可以有返回值的启动一个协程：使用await方法；
	- 可以在用到返回值的时候再调用.await；
- withContext
	- 通过输入Dispatcher，转换协程的运行线程；
	- 有返回值，返回前挂起外部协程等待结果；
	- 挂起函数；

### 发布协程到线程

- Dispatchers.Default
	默认线程，适用于低并发，大计算场景；
- Dispatchers.IO
	高并发低计算场景；
- Dispatchers.Main
	安卓中主线程；

### 其他

- suspendCoroutine
- 