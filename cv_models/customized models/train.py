import torch
from torch import nn
from torchsummary import summary
from torchvision import transforms, datasets
from torch.utils.data import DataLoader
from tqdm import tqdm
import math


BATCH_SIZE = 64
EPOCH = 10
DATA_PATH = r'D:\my_phd\on_git\test\data'
MODEL_WEIGHTS = r'model.pth'


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 6, 5, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(6, 16, 5),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.classifiers = nn.Sequential(
            nn.Linear(400, 120),
            nn.ReLU(),

            nn.Linear(120, 84),
            nn.ReLU(),

            nn.Linear(84, 10)
        )

    def forward(self, x):
        feature = self.features(x)
        feature = feature.view(x.shape[0], -1)
        out = self.classifiers(feature)
        return out


def get_dataloader(shuffle=True):
    transformer = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    train_set = datasets.MNIST(DATA_PATH, train=True, transform=transformer, download=False)
    test_set = datasets.MNIST(DATA_PATH, train=False, transform=transformer, download=False)

    train_loader = DataLoader(train_set, BATCH_SIZE, shuffle=shuffle)
    test_loader = DataLoader(test_set, BATCH_SIZE, shuffle=shuffle)

    return train_loader, test_loader


def train(model, train_loader, epoch):
    model.train()
    total_batch = len(train_loader)

    for batch_i, (X, y) in enumerate(train_loader):
        out = model(X)
        cur_loss = loss_fn(out, y)

        optimizer.zero_grad()
        cur_loss.backward()
        optimizer.step()

        _, pred = torch.max(out, axis=1)

        if batch_i % 100 == 0:
            print(f"Epoch:{epoch}, Batch: {batch_i}/{total_batch}, loss:{cur_loss.item():.5f}")


def test(model, test_loader):
    model.eval()
    test_loss, test_correct, test_acc = 0.0, 0, 0.0
    test_size = len(test_loader.dataset)

    state_dict = {
        'model': model.state_dict(),
        'acc': test_correct
    }
    with torch.no_grad():
        for X, y in test_loader:
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            test_correct += torch.sum(pred.argmax(1) == y)
        test_acc = test_correct / test_size
    print(f"Test loss:{test_loss:>.5f}, Test Accuracy:{test_acc.item():>.4f}")
    if test_acc > best_acc:
        state_dict['acc'] = test_acc
        torch.save(state_dict, 'model.pth')


def load_model():
    model = Net()
    checkpoint = torch.load(MODEL_WEIGHTS)
    model.load_state_dict(checkpoint['model'])
    # accuracy = checkpoint['acc']
    # _, test_loader = get_dataloader()
    # test(model, test_loader)
    return model



if __name__ == '__main__':
    model = Net()
    # summary(model, (1, 28, 28), 4)

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

    train_loader, test_loader = get_dataloader()

    best_acc = 0.0
    # for epoch_i in range(EPOCH):
    #     train(model, train_loader, epoch_i)
    #     test(model, test_loader)
    load_model()



























