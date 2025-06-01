import numpy as np
import matplotlib.pyplot as plt

class SimpleNeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        """
        初始化神经网络
        input_size: 输入层大小
        hidden_size: 隐藏层大小  
        output_size: 输出层大小
        """
        # 随机初始化权重，使用较小的值避免梯度消失
        self.W1 = np.random.randn(input_size, hidden_size) * 0.5
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.5
        self.b2 = np.zeros((1, output_size))
        
    def sigmoid(self, x):
        """Sigmoid激活函数，将输出压缩到0-1之间"""
        # 防止数值溢出
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))
    
    def sigmoid_derivative(self, x):
        """Sigmoid函数的导数，用于反向传播"""
        return x * (1 - x)
    
    def forward(self, X):
        """
        前向传播：输入数据通过网络得到输出
        X: 输入数据
        """
        # 第一层：输入层到隐藏层
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        
        # 第二层：隐藏层到输出层
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.sigmoid(self.z2)
        
        return self.a2
    
    def backward(self, X, y, output):
        """
        反向传播：计算梯度并更新权重
        X: 输入数据
        y: 真实标签
        output: 网络输出
        """
        m = X.shape[0]  # 样本数量
        
        # 计算输出层误差
        self.output_error = y - output
        self.output_delta = self.output_error * self.sigmoid_derivative(output)
        
        # 计算隐藏层误差
        self.z1_error = self.output_delta.dot(self.W2.T)
        self.z1_delta = self.z1_error * self.sigmoid_derivative(self.a1)
        
        # 更新权重和偏置
        self.W1 += X.T.dot(self.z1_delta) / m
        self.b1 += np.sum(self.z1_delta, axis=0, keepdims=True) / m
        self.W2 += self.a1.T.dot(self.output_delta) / m
        self.b2 += np.sum(self.output_delta, axis=0, keepdims=True) / m
    
    def train(self, X, y, epochs):
        """训练网络"""
        losses = []
        
        for i in range(epochs):
            # 前向传播
            output = self.forward(X)
            
            # 计算损失（均方误差）
            loss = np.mean(np.square(y - output))
            losses.append(loss)
            
            # 反向传播
            self.backward(X, y, output)
            
            # 每1000次迭代打印一次损失
            if i % 1000 == 0:
                print(f"Epoch {i}, Loss: {loss:.6f}")
        
        return losses

# 创建训练数据（XOR问题）
X = np.array([[0, 0],
              [0, 1], 
              [1, 0],
              [1, 1]])

y = np.array([[0],
              [1],
              [1], 
              [0]])

# 创建网络实例
nn = SimpleNeuralNetwork(input_size=2, hidden_size=4, output_size=1)

# 训练网络
print("开始训练...")
losses = nn.train(X, y, epochs=10000)

# 测试网络
print("\n训练完成，测试结果：")
predictions = nn.forward(X)
for i in range(len(X)):
    print(f"输入: {X[i]}, 真实输出: {y[i][0]}, 预测输出: {predictions[i][0]:.4f}")

# 绘制损失曲线
plt.figure(figsize=(10, 6))
plt.plot(losses)
plt.title('训练损失曲线')
plt.xlabel('迭代次数')
plt.ylabel('损失值')
plt.grid(True)
plt.show()