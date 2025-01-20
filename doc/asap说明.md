# 关于 ASAP 的说明

## 一、获取

ASAP 全称 Automated Slide Analysis Platform，是一种层级图像读取工具，在 Windows 和 Linux 上均有支持
 - [点击前往官方仓库](https://github.com/computationalpathologygroup/ASAP)
 - [点击前往下载链接](https://github.com/computationalpathologygroup/ASAP/releases)

本仓库编写时所用版本为 ASAP v2.2.0

## 二、使用

ASAP 可以作为一个软件使用，用于访问 '.tif' 或 '.svs' 格式的包含层级信息的图像

本仓库对 ASAP 的使用更多在代码层面，这需要获得 ASAP 对 Python 的支持

在安装目录中，你可以找到一个名为 ```multiresolutionimageinterface.py``` 的文件，它是 ASAP 提供的 Python 接口

为了在 Python 代码中正常访问这些接口，我们需要将 ASAP 的安装路径加载到 Python 的运行时环境中去

具体的说，这需要 ASAP 的安装路径出现在 Python 运行时的 ```sys.path``` 中

## 三、运行配置（运行时不报错）

只要在 ```import multiresolutionimageinterface``` 之前将路径加载到 ```sys.path``` 中即可，为此，我们有如下方案：
 - 手动在代码中加入：
   - ```import sys; sys.path.append(path)```
 - 在 Pycharm 的启动模板中加入：
   - setting / build / console / python console / starting script
 - 在 Pycharm 的项目路径配置中加入：
   - setting / project / project structure / add content root
 - 在 Python 的库依赖中加入：
   - python 安装目录 / site-packages / my_lib.pth:: ```path```
 - 在系统环境变量中加入：
   - Windows / 环境变量 / PYTHON 或者 PYTHONPATH
   - Linux / 用户目录 / .bashrc
   
## 四、解释器配置（敲代码时不飘红）

可以在 setting / project / project interpreter / show all / interpreter paths 中加入路径
