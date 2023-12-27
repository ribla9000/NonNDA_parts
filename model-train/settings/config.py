import torch,  os
from transformers import VisionEncoderDecoderConfig


max_length = 768
image_size = [720, 1280]
train_config = {"max_epochs":10000,
          "val_check_interval":0.4,
          "check_val_every_n_epoch":1,
          "gradient_clip_val":1.0,
          "num_training_samples_per_epoch": 720,
          "lr": 2e-5,
          "train_batch_sizes": [10],
          "val_batch_sizes": [2],
          "num_nodes": 1,
          "warmup_steps": 108,
          "result_path": "./result",
          "verbose": False
          }


def get_options():
    torch.set_float32_matmul_precision("medium")
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    model_config = VisionEncoderDecoderConfig.from_pretrained("")
    model_config.encoder.image_size = image_size
    model_config.decoder.max_length = max_length
    token = os.getenv("NOD")
    return model_config
