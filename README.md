# 1. 模块介绍
## qq_email_download.py:  qq邮箱的登录模块 图片下载
## qq_email_2.py:  qq邮箱的登录测试
## imgs_tools.py:  图片处理切割工具
## feature.py： 图片特征提取
## train.py:  提供模型训练.测试
## mx_model.py: 模型的加载模块
## cfg.py:  一些路径配置
## data/bin_img/ :  存放 灰度/二值化后的图片
## data/cut_pic/ :  存放分割后的图片
## data/knn_train/ : 存放模型和特征文件
## data/origin_img/ : 存放下载原图
## data/test_pic/ : 存放测试集图片

# 2 图片预处理
 * 登录使用的是selenium,此处不予多说
 * 图片下载来以后大小是680*390的,在浏览器上是以280*158显示,所以图片需转换一下大小.
 * 因小图在大图上的横坐标是固定的18像素,故不考虑小图的作用,只需分析目标图在大图中的横坐标即可
 * 拿到图片后,首先是把大小变成280*158,转灰度图

# 3 图片切割
    目标区域为44*44的区域,我选择的是以目标区域的1/3长度为步长,循环截取灰度图,最终每张图得到144个小图
    每张图的名字就是其左上角点的坐标
    结果就是一张bin_img/xxxx.png 就变成144张类似  cut_pic/xxxx.png/(78,42).png ....  的图片
# 4 打标签
    打标签是最痛苦的一步了,
    但是在这里为了消除人工误差,我采取的是将截取出来的144张小图,观察目标图是否在小图区域内.
    若目标区域出现在目标区域内:若是目标区域距离小图的四条边的距离<=10个像素则会采用,
    标签我是根据目标区域在小图中的像素位移值来修改其名字,
    如 (190, 56)+8.png , (204, 56)+6.png
    分别代表目标区域在此图左移了 8,-6 个像素
    ps: 别嫌这样麻烦,最初我只是根据感觉标记,但发现结果出来的误差比较大,只有这样标记几乎不会有误差
# 5. 特征的提取
    特征提取就是将每张小图,转为一维数组(1936个元素)=>x,自己标记的位移向量=>y
    其他的图片y=99
    这样我跑数据的时候,就可以只选取识别出位移量(!=99)的图片,在与其名字(坐标)相加,就可以算出识别出来的目标区域横坐标
    ps: 我试过将图片的特征减少一些,比如采用相邻的四个像素缩放成一个像素,取其灰度值的平均值,
        但后来发现同样会丢失精度,作罢,特征值多些就多些吧,总算对速度影响还在接受范围

# 6. 模型

    最初我选择的是knn/svm算法,但是发现随着我的测试样本的数量增加,模型出来后,模型的速度很慢,也很吃内存

    因邮箱滑块滑动的时候本来是允许可以几个像素的误差的.
    在此每张原图对应的144张小图,识别出来的所有横坐标取其平均值来降低误差
    最终逻辑回归,即便使用逻辑回归,最终预测结果精准识别的也达到90%以上

## 在此要感谢 哈莫 我做滑块识别最初是一头雾水,结合哈莫的这篇博客
[字符型图片验证码识别完整过程及Python实现](http://www.cnblogs.com/beer/p/5672678.htm)
## 我作出了我的第一个简单的字母型验证码识别,才有了我的这个项目

