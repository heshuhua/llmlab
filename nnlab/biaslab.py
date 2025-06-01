import numpy as np
import matplotlib.pyplot as plt
class BiasDemo:
    def __init__(self, use_bias=True):
        self.use_bias = use_bias
        self.weight = np.random.randn() * 0.5
        if use_bias:
            self.bias = np.random.randn() * 0.5
        else:
            self.bias = 0
    
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def forward(self, x):
        if self.use_bias:
            return self.sigmoid(self.weight * x + self.bias)
        else:
            return self.sigmoid(self.weight * x)
    
    def train(self, X, y, epochs=1000, lr=1.0):
        losses = []
        for epoch in range(epochs):
            # 前向传播
            predictions = np.array([self.forward(x) for x in X])
            
            # 计算损失
            loss = np.mean((y - predictions) ** 2)
            losses.append(loss)
            
            # 简单的梯度下降更新
            error = y - predictions
            
            # 更新权重
            weight_grad = np.mean(error * predictions * (1 - predictions) * X)
            self.weight += lr * weight_grad
            
            # 更新偏置（如果使用）
            if self.use_bias:
                bias_grad = np.mean(error * predictions * (1 - predictions))
                self.bias += lr * bias_grad
        
        return losses

# 创建测试数据 - 这个数据需要偏置才能很好地拟合
X = np.array([0, 1, 2, 3, 4])
y = np.array([0.8, 0.9, 0.95, 0.98, 0.99])  # 注意：即使输入为0，输出也不为0

# 训练两个模型：一个有偏置，一个没有
model_with_bias = BiasDemo(use_bias=True)
model_without_bias = BiasDemo(use_bias=False)

losses_with = model_with_bias.train(X, y)
losses_without = model_without_bias.train(X, y)

# 比较结果
print("训练结果比较：")
print(f"有偏置模型 - 权重: {model_with_bias.weight:.3f}, 偏置: {model_with_bias.bias:.3f}")
print(f"无偏置模型 - 权重: {model_without_bias.weight:.3f}, 偏置: 0")

print("\n预测结果对比：")
for i, x_val in enumerate(X):
    pred_with = model_with_bias.forward(x_val)
    pred_without = model_without_bias.forward(x_val)
    print(f"输入: {x_val}, 真实值: {y[i]:.3f}, 有偏置: {pred_with:.3f}, 无偏置: {pred_without:.3f}")

# 绘制对比图
plt.figure(figsize=(15, 5))

# 训练过程对比
plt.subplot(1, 3, 1)
plt.plot(losses_with, label='有偏置', color='blue')
plt.plot(losses_without, label='无偏置', color='red')
plt.xlabel('训练轮次')
plt.ylabel('损失')
plt.title('训练损失对比')
plt.legend()
plt.grid(True)

# 拟合效果对比
plt.subplot(1, 3, 2)
x_test = np.linspace(-1, 5, 100)
y_pred_with = [model_with_bias.forward(x) for x in x_test]
y_pred_without = [model_without_bias.forward(x) for x in x_test]

plt.plot(x_test, y_pred_with, 'b-', label='有偏置预测', linewidth=2)
plt.plot(x_test, y_pred_without, 'r--', label='无偏置预测', linewidth=2)
plt.scatter(X, y, color='green', s=100, label='真实数据', zorder=5)
plt.xlabel('输入')
plt.ylabel('输出')
plt.title('拟合效果对比')
plt.legend()
plt.grid(True)

# 激活函数的移位效果
plt.subplot(1, 3, 3)
x_range = np.linspace(-3, 3, 100)
sigmoid_normal = 1 / (1 + np.exp(-x_range))
sigmoid_shifted = 1 / (1 + np.exp(-(x_range - 1.5)))  # 偏置=1.5的效果

plt.plot(x_range, sigmoid_normal, 'b-', label='sigmoid(x) - 无偏置')
plt.plot(x_range, sigmoid_shifted, 'r-', label='sigmoid(x-1.5) - 有偏置')
plt.axhline(y=0.5, color='gray', linestyle=':', alpha=0.7)
plt.axvline(x=0, color='gray', linestyle=':', alpha=0.7, label='x=0')
plt.axvline(x=1.5, color='orange', linestyle=':', alpha=0.7, label='新的中心点')
plt.xlabel('输入')
plt.ylabel('输出')
plt.title('偏置如何移位激活函数')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()