import hydra

from dataloader import get_dataloader, load
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.loggers.wandb import WandbLogger
from models.MainModel_PL import PLRecommand

import numpy as np


@hydra.main(config_name="config.yml")
def main(cfg):
    # dataloader
    train_dataset, eval_dataset = load(**cfg.DATASETS)
    
    train_dataloader = get_dataloader(train_dataset, **cfg.DATALOADER)
    eval_dataloader = get_dataloader(eval_dataset, **cfg.DATALOADER)
    
    # model
    cfg.OPTIMIZER['num_train_steps']= len(train_dataloader) * cfg.TRAININGARGS.max_epochs
    model = PLRecommand(cfg.MODEL, cfg.OPTIMIZER)

    # logs
    wandb_logger = WandbLogger(**cfg.PATH.wandb)
    callbacks = [ModelCheckpoint(**cfg.PATH.ckpt)]

    # trainer
    trainer = Trainer(
        callbacks=callbacks,
        logger=wandb_logger,
        **cfg.TRAININGARGS,
    )
    trainer.fit(model, train_dataloader, eval_dataloader)

if __name__ == "__main__":
    main()