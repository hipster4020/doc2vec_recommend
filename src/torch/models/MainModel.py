import torch
import torch.nn as nn


class RecommandModel(nn.Module):
    def __init__(
        self,
        input_size,
        hidden_size,
        dropout,
    ):
        super().__init__()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

        self.rnn = nn.RNN(input_size, hidden_size, batch_first=True)
        self.target_layer = nn.Linear(input_size, hidden_size)
        self.hidden_layer = nn.Linear(hidden_size, hidden_size)
        self.final_layer = nn.Linear(hidden_size, 1)
    
    def forward(self, input, target):
        # rnn
        outputs, _status = self.rnn(input)
        # rnn = self.hidden_layer(outputs[:, -1, :])
        # rnn = self.relu(rnn)
        # rnn = self.dropout(rnn)

        # target
        target_outputs = self.target_layer(target)
        # target = self.hidden_layer(target_outputs)
        # target = self.relu(target)
        # target = self.dropout(target)

        # outputs = rnn + target

        outputs = outputs[:, -1, :] + target_outputs

        src = self.hidden_layer(outputs)
        src = self.relu(src)
        src = self.dropout(src)

        src = self.final_layer(src)
        src = self.sigmoid(src)
        
        return src