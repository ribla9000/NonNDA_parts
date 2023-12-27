from datasets import load_dataset
from transformers import DonutProcessor, VisionEncoderDecoderModel
from settings.config import max_length, image_size, get_options
from repository.train import DonutDataset


def set_pre_train(model: str = ""):
    model_config_ = get_options()
    processor = DonutProcessor.from_pretrained(model)
    _model = VisionEncoderDecoderModel.from_pretrained(model, config=model_config_)
    processor.feature_extractor.size = image_size[::-1]
    processor.feature_extractor.do_align_long_axis = False
    return processor, _model


def run_dataset(model: str = "",
                dataset: str = ""):
    processor, _model = set_pre_train(model)
    train_dataset = DonutDataset(dataset, max_length=max_length,
                                 split="train", task_start_token="<s_cord-v2>", prompt_end_token="<s_cord-v2>",
                                 sort_json_key=False, processor=processor, model=_model)
    val_dataset = DonutDataset(dataset, max_length=max_length,
                               split="validation", task_start_token="<s_cord-v2>", prompt_end_token="<s_cord-v2>",
                               sort_json_key=False, processor=processor, model=_model)
    
    return train_dataset, val_dataset, processor, _model
