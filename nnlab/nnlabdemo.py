import torch
import torch.nn as nn
import torch.optim as optim

class SimpleNet(nn.Module):
    def __init__(self, in_dim,hidden_dim,out_dim):
        super().__init__()
        self.fc1=nn.Linear(in_dim,hidden_dim)
        self.relu=nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, out_dim)
    
    def forward(self,x):
        x=self.relu(self.fc1(x))
        return self.fc2(x)
model = SimpleNet(in_dim=4, hidden_dim=8, out_dim=2)

# 2) 查看模型参数
for name, param in model.named_parameters():
    print(f"{name:10s} | shape: {tuple(param.shape)}")


# 创建一个假的数据集
X = torch.randn(100, 4)            # 100 个样本，每个 4 维
y = torch.randint(0, 2, (100,))    # 二分类标签 0 或 1

# 损失与优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# 简单训练若干轮
for epoch in range(5):
    logits = model(X)
    loss = criterion(logits, y)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

# 保存模型文件（只保存参数）
torch.save(model.state_dict(), "simple_net.pth")
print("模型已保存到 simple_net.pth")

model2 = SimpleNet(4, 8, 2)
model2.load_state_dict(torch.load("simple_net.pth"))
model2.eval()