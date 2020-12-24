import torch.nn.functional as F


# deeper model adapted from https://www.kaggle.com/gustafsilva/cnn-digit-recognizer-pytorch
class Net(nn.Module):
    def __init__(self, with_ReLU=True, with_BatchNorm=True, with_MaxPool=True, with_Dropout=True):
        super(Net, self).__init__()

        self.with_ReLU = with_ReLU
        self.with_BatchNorm = with_BatchNorm
        self.with_MaxPool = with_MaxPool
        self.with_Dropout = with_Dropout

        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 32, 3, stride=2, padding=1)

        self.conv4 = nn.Conv2d(32, 64, 3, padding=1)
        self.conv5 = nn.Conv2d(64, 64, 3, padding=1)
        self.conv6 = nn.Conv2d(64, 64, 3, stride=2, padding=1)

        self.fc1 = nn.Linear(16 * 2 * 2, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):

        def apply(x, with_ReLU=False, with_BatchNorm=None, with_MaxPool=None, with_Dropout=None):
            if with_ReLU:
                x = F.relu(x)
            if with_BatchNorm is not None:
                n_chans = x.shape[1]
                running_mu = torch.zeros(n_chans).to(device)  # zeros are fine for first training iter
                running_std = torch.ones(n_chans).to(device)  # ones are fine for first training iter
                x = F.batch_norm(x, running_mu, running_std, training=True, momentum=0.9)
            if with_MaxPool is not None:
                x = F.max_pool2d(x, with_MaxPool[0], with_MaxPool[1])
            if with_Dropout is not None:
                x = F.dropout(with_Dropout)
            return x

        x = apply(self.conv1(x), with_ReLU=self.with_ReLU,
                  with_BatchNorm=32 if self.with_BatchNorm else None,
                  with_MaxPool=None, with_Dropout=None)

        x = apply(self.conv2(x), with_ReLU=self.with_ReLU,
                  with_BatchNorm=32 if self.with_BatchNorm else None,
                  with_MaxPool=None, with_Dropout=None)

        x = apply(self.conv3(x), with_ReLU=self.with_ReLU,
                  with_BatchNorm=32 if self.with_BatchNorm else None,
                  with_MaxPool=(2, 2) if self.with_MaxPool else None,
                  with_Dropout=0.25 if self.with_Dropout else None)

        x = apply(self.conv4(x), with_ReLU=self.with_ReLU,
                  with_BatchNorm=64 if self.with_BatchNorm else None,
                  with_MaxPool=None, with_Dropout=None)

        x = apply(self.conv5(x), with_ReLU=self.with_ReLU,
                  with_BatchNorm=64 if self.with_BatchNorm else None,
                  with_MaxPool=None, with_Dropout=None)

        x = apply(self.conv6(x), with_ReLU=self.with_ReLU,
                  with_BatchNorm=64 if self.with_BatchNorm else None,
                  with_MaxPool=(2, 2) if self.with_MaxPool else None,
                  with_Dropout=0.25 if self.with_Dropout else None)

        x = x.view(x.size(0), -1)

        x = apply(self.fc1(x), with_ReLU=self.with_ReLU,
                  with_BatchNorm=32 if self.with_BatchNorm else None,
                  with_MaxPool=None, with_Dropout=None)

        x = apply(self.fc2(x), with_ReLU=self.with_ReLU,
                  with_BatchNorm=32 if self.with_BatchNorm else None,
                  with_MaxPool=None, with_Dropout=None)

        x = apply(self.fc3(x), with_ReLU=False, with_BatchNorm=None,
                  with_MaxPool=None, with_Dropout=None)

        x = F.log_softmax(x, dim=1)
        return x
