from torch.utils.data import DataLoader
from pytorch_lightning.loggers import WandbLogger
import pytorch_lightning as pl
from repository.train import DonutModelPLModule, PushToHubCallback
from repository.pre_train import run_dataset
from settings.config import train_config
from huggingface_hub import login
import wandb


def run_training():
    login("")
    wandb.login()
    train_dataset, val_dataset, processor, model = run_dataset()
    train_dataloader = DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=6)
    val_dataloader = DataLoader(val_dataset, batch_size=2, shuffle=False, num_workers=2)
    model.config.pad_token_id = processor.tokenizer.pad_token_id
    model.config.decoder_start_token_id = processor.tokenizer.convert_tokens_to_ids(['<s_cord-v2>'])[0]
    model_module = DonutModelPLModule(
        train_config,
        processor,
        model,
        train_dataloader=train_dataloader,
        val_dataloader=val_dataloader
    )

    wandb_logger = WandbLogger(project="TableExtractor", name="TableExtractor")
    trainer = pl.Trainer(
        accelerator="gpu",
        devices=1,
        max_epochs=train_config.get("max_epochs"),
        val_check_interval=train_config.get("val_check_interval"),
        check_val_every_n_epoch=train_config.get("check_val_every_n_epoch"),
        gradient_clip_val=train_config.get("gradient_clip_val"),
        precision=16,
        num_sanity_val_steps=0,
        logger=wandb_logger,
        callbacks=[PushToHubCallback()]
    )
    trainer.fit(model_module)
