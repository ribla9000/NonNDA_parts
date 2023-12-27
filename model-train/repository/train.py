from torch.utils.data import Dataset
from datasets import load_dataset
import torch, json, random, re, gc
from typing import Any, List, Tuple, Optional
from transformers import DonutProcessor, VisionEncoderDecoderModel
import pytorch_lightning as pl
from nltk import edit_distance
from pytorch_lightning.callbacks import Callback
from settings.config import max_length
import numpy as np


added_tokens = []


class DonutDataset(Dataset):

    def __init__(
        self,
        dataset_name_or_path: str,
        max_length: int,
        split: str = "train",
        ignore_id: int = -100,
        task_start_token: str = "<s>",
        prompt_end_token: str = None,
        sort_json_key: bool = True,
        processor: DonutProcessor = None,
        model: VisionEncoderDecoderModel = None
    ):
        super().__init__()
        
        self.model = model
        self.processor = processor
        self.max_length = max_length
        self.split = split
        self.ignore_id = ignore_id
        self.task_start_token = task_start_token
        self.prompt_end_token = prompt_end_token if prompt_end_token else task_start_token
        self.sort_json_key = sort_json_key
        self.dataset = load_dataset(dataset_name_or_path, split=self.split)
        self.dataset_length = len(self.dataset)

        self.gt_token_sequences = []
        for sample in self.dataset:
            ground_truth = json.loads(sample["ground_truth"])
            if "gt_parses" in ground_truth:
                assert isinstance(ground_truth["gt_parses"], list)
                gt_jsons = ground_truth["gt_parses"]
            else:
                assert "gt_parse" in ground_truth and isinstance(ground_truth["gt_parse"], dict)
                gt_jsons = [ground_truth["gt_parse"]]

            self.gt_token_sequences.append(
                [
                    self.json2token(
                        gt_json,
                        update_special_tokens_for_json_key=self.split == "train",
                        sort_json_key=self.sort_json_key,
                    )
                    + self.processor.tokenizer.eos_token
                    for gt_json in gt_jsons
                ]
            )

        self.add_tokens([self.task_start_token, self.prompt_end_token])
        self.prompt_end_token_id = self.processor.tokenizer.convert_tokens_to_ids(self.prompt_end_token)

    def json2token(self, obj: Any, update_special_tokens_for_json_key: bool = True, sort_json_key: bool = True):

        if type(obj) == dict:
            if len(obj) == 1 and "text_sequence" in obj:
                return obj["text_sequence"]
            else:
                output = ""
                if sort_json_key:
                    keys = sorted(obj.keys(), reverse=True)
                else:
                    keys = obj.keys()
                for k in keys:
                    if update_special_tokens_for_json_key:
                        self.add_tokens([fr"<s_{k}>", fr"</s_{k}>"])
                    output += (
                        fr"<s_{k}>"
                        + self.json2token(obj[k], update_special_tokens_for_json_key, sort_json_key)
                        + fr"</s_{k}>"
                    )
                return output
        elif type(obj) == list:
            return r"<sep/>".join(
                [self.json2token(item, update_special_tokens_for_json_key, sort_json_key) for item in obj]
            )
        else:
            obj = str(obj)
            if f"<{obj}/>" in added_tokens:
                obj = f"<{obj}/>"
            return obj

    def add_tokens(self, list_of_tokens: List[str]):

        newly_added_num = self.processor.tokenizer.add_tokens(list_of_tokens)
        if newly_added_num > 0:
            self.model.decoder.resize_token_embeddings(len(self.processor.tokenizer))
            added_tokens.extend(list_of_tokens)

    def __len__(self) -> int:
        return self.dataset_length

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        sample = self.dataset[idx]

        pixel_values = self.processor(sample["image"], random_padding=self.split == "train", return_tensors="pt").pixel_values
        pixel_values = pixel_values.squeeze()
        target_sequence = random.choice(self.gt_token_sequences[idx])
        input_ids = self.processor.tokenizer(
            target_sequence,
            add_special_tokens=False,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )["input_ids"].squeeze(0)

        labels = input_ids.clone()
        labels[labels == self.processor.tokenizer.pad_token_id] = self.ignore_id
        return pixel_values, labels, target_sequence


class DonutModelPLModule(pl.LightningModule):
    
    def __init__(self, config, processor, model, train_dataloader, val_dataloader):
        super().__init__()
        self.config = config
        self.processor = processor
        self.model = model
        self.train_data = train_dataloader
        self.val_data = val_dataloader

    def training_step(self, batch, batch_idx):
        pixel_values, labels, _ = batch
        outputs = self.model(pixel_values, labels=labels)
        loss = outputs.loss
        self.log_dict({"train_loss": loss}, sync_dist=True)
        return loss

    def validation_step(self, batch, batch_idx, dataset_idx=0):
        pixel_values, labels, answers = batch
        batch_size = pixel_values.shape[0]
        decoder_input_ids = torch.full((batch_size, 1), self.model.config.decoder_start_token_id, device=self.device)

        outputs = self.model.generate(
            pixel_values,
            decoder_input_ids=decoder_input_ids,
            max_length=max_length,
            early_stopping=True,
            pad_token_id=self.processor.tokenizer.pad_token_id,
            eos_token_id=self.processor.tokenizer.eos_token_id,
            use_cache=True,
            num_beams=1,
            bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True,
        )

        predictions = []
        for seq in self.processor.tokenizer.batch_decode(outputs.sequences):
            seq = seq.replace(self.processor.tokenizer.eos_token, "").replace(self.processor.tokenizer.pad_token, "")
            seq = re.sub(r"<.*?>", "", seq, count=1).strip()  # remove first task start token
            predictions.append(seq)

        scores = list()
        for pred, answer in zip(predictions, answers):
            pred = re.sub(r"(?:(?<=>) | (?=</s_))", "", pred)
            answer = answer.replace(self.processor.tokenizer.eos_token, "")
            scores.append(edit_distance(pred, answer) / max(len(pred), len(answer)))

            if self.config.get("verbose", False) and len(scores) == 1:
                print(f"Prediction: {pred}")
                print(f"    Answer: {answer}")
                print(f" Normed ED: {scores[0]}")

        return scores

    def validation_epoch_end(self, validation_step_outputs):
        num_of_loaders = 1
        if num_of_loaders == 1:
            validation_step_outputs = [validation_step_outputs]
        assert len(validation_step_outputs) == num_of_loaders
        cnt = [0] * num_of_loaders
        total_metric = [0] * num_of_loaders
        val_metric = [0] * num_of_loaders
        for i, results in enumerate(validation_step_outputs):
            for scores in results:
                cnt[i] += len(scores)
                total_metric[i] += np.sum(scores)
            val_metric[i] = total_metric[i] / cnt[i]
            val_metric_name = f"val_metric_{i}th_dataset"
            self.log_dict({val_metric_name: val_metric[i]}, sync_dist=True)
        self.log_dict({"val_metric": np.sum(total_metric) / np.sum(cnt)}, sync_dist=True)

    def configure_optimizers(self):
        gc.collect()
        optimizer = torch.optim.Adam(self.parameters(), lr=self.config.get("lr"))
        return optimizer

    def train_dataloader(self):
        return self.train_data

    def val_dataloader(self):
        return self.val_data


class PushToHubCallback(Callback):

    def on_train_epoch_end(self, trainer, pl_module):
        gc.collect()
        print(f"\nCurrent Epoch!!! {trainer.current_epoch}")
        if trainer.current_epoch % 5 == 0 and trainer.current_epoch != 0:
            try:
                if trainer.current_epoch % 10 and trainer.current_epoch != 0:
                    pl_module.processor.push_to_hub("",
                                                    commit_message=f"{trainer.current_epoch}")
                    pl_module.model.push_to_hub("",
                                                commit_message=f"{trainer.current_epoch}")

            except:
                print("---" * 6 + "\n" + "Unable to push model to the hub, SOME ERROR." + "\n" + "---" * 6)
                pass
    
    def on_train_end(self, trainer, pl_module):
        try:
            print(f"\nPushing model to the hub after training")
            pl_module.processor.push_to_hub("",
                                            commit_message=f"Training done")
            pl_module.model.push_to_hub("",
                                        commit_message=f"Training done")
            gc.collect()

        except:
            print(
                "---" * 6 + "\n" + "Unable to push model to the hub, SOME ERROR. TRYING AGAIN [TRAIN END]" + "\n" + "---" * 6)
            gc.collect()
            self.on_train_end(trainer=trainer, pl_module=pl_module)
