
from nn2demo import SimpleNet
model2 = SimpleNet(4, 8, 2)
model2.load_state_dict(torch.load("simple_net.pth"))
model2.eval()
