import numpy as np
import matplotlib.pyplot as plt

# 创建示例数据
x = np.array([1, 2, 3, 4, 5])
y_with_intercept = np.array([7, 9, 11, 13, 15])  # y = 2x + 5
y_without_intercept = np.array([2, 4, 6, 8, 10])  # y = 2x

plt.figure(figsize=(12, 5))

# 有截距的情况
plt.subplot(1, 2, 1)
plt.scatter(x, y_with_intercept, color='red', s=50)
plt.plot(x, 2*x + 5, 'b-', label='y = 2x + 5 (有截距)')
plt.plot(x, 2*x, 'g--', label='y = 2x (无截距)')
plt.xlabel('x')
plt.ylabel('y')
plt.title('截距的作用')
plt.legend()
plt.grid(True)

# 神经元输出对比
plt.subplot(1, 2, 2)
x_range = np.linspace(-2, 2, 100)
y_with_bias = 1 / (1 + np.exp(-(2*x_range + 1)))  # 有偏置
y_without_bias = 1 / (1 + np.exp(-2*x_range))      # 无偏置

plt.plot(x_range, y_with_bias, 'b-', label='have (sigmoid(2x+1))')
plt.plot(x_range, y_without_bias, 'r--', label='no (sigmoid(2x))')
plt.axhline(y=0.5, color='gray', linestyle=':', alpha=0.7)
plt.axvline(x=0, color='gray', linestyle=':', alpha=0.7)
plt.xlabel('input')
plt.ylabel('out')
plt.title('pianzhi')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()