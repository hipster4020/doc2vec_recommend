from typing import Dict, Union

import torch
import torch.nn as nn
from pytorch_lightning import LightningModule

from models.MainModel import RecommandModel
from transformers import get_cosine_schedule_with_warmup

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class PLRecommand(LightningModule):
    def __init__(
        self,
        config: Dict,
        optimizer_config: Dict,
        class_weight: Union[int, float] = 8,
    ):
        super().__init__()
        self.save_hyperparameters()
        
        self.model = RecommandModel(**config)
        self.optimizer_config = optimizer_config

        self.criterion = nn.BCELoss()

    def forward(self, input, target):
        return self.model(input, target)

    def training_step(self, batch, batch_idx):
        pos_pred = self(batch['input'], batch['target'])
        neg_pred = self(batch['input'], batch['negative_target'])

        pos_loss = self.criterion(pos_pred, torch.ones(pos_pred.shape).to(device))
        neg_loss = self.criterion(neg_pred, torch.zeros(neg_pred.shape).to(device))
        loss = pos_loss + neg_loss

        log_dict = {
            "train/pos_loss": pos_loss,
            "train/neg_loss": neg_loss,
            "train/loss": loss,
        }
        self.log_dict(log_dict, on_epoch=True)

        return loss

    def validation_step(self, batch, batch_idx):
        pos_pred = self(batch['input'], batch['target'])
        neg_pred = self(batch['input'], batch['negative_target'])

        pos_loss = self.criterion(pos_pred, torch.ones(pos_pred.shape).to(device))
        neg_loss = self.criterion(neg_pred, torch.zeros(neg_pred.shape).to(device))
        loss = pos_loss + neg_loss

        log_dict = {
            "eval/pos_loss": pos_loss,
            "eval/neg_loss": neg_loss,
            "eval/loss": loss,
        }
        self.log_dict(log_dict, on_epoch=True)

        return loss

    def configure_optimizers(self):
        # optimizer
        optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.optimizer_config["lr"],
        )
        print(f"num_train_steps : {self.optimizer_config['num_train_steps']}")
        # lr scheduler
        num_warmup_steps = int(self.optimizer_config["num_train_steps"] * self.optimizer_config["warmup_ratio"])
        scheduler = get_cosine_schedule_with_warmup(
            optimizer,
            num_warmup_steps=num_warmup_steps,
            num_training_steps=self.optimizer_config["num_train_steps"],
        )
        lr_scheduler = {
            'scheduler': scheduler,
            'name': 'cosine_schedule_with_warmup',
            'monitor': 'loss',
            'interval': 'step',
            'frequency': 1,
        }

        return [optimizer], [lr_scheduler]
