import torch
import os
from peft import PeftModel
from transformers import AutoTokenizer

from tinychart.model.builder import load_pretrained_model
from tinychart.mm_utils import get_model_name_from_path
from tinychart.eval.run_tiny_chart import inference_model


class TinyChartInference:

    def __init__(
        self,
        base_model="mPLUG/TinyChart-3B-768",
        lora_model="shiinn97/tinychart3B-indochartqa",
        hf_token = os.getenv("HF_TOKEN"),
        device=None,
    ):

        self.base_model = base_model
        self.lora_model = lora_model
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        print("=" * 60)
        print("Loading TinyChart...")
        print("=" * 60)

        # tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.lora_model,
            token=""
        )

        # base model
        _, model, image_processor, context_len = load_pretrained_model(
            self.base_model,
            model_base=None,
            model_name=get_model_name_from_path(self.base_model),
            device=self.device,
        )

        # load LoRA
        model = PeftModel.from_pretrained(
            model,
            self.lora_model,
            token=hf_token
        )

        print("Merging LoRA adapter...")

        model = model.merge_and_unload()

        model.eval()

        self.model = model
        self.image_processor = image_processor
        self.context_len = context_len

        print("TinyChart is ready!")

    def predict(
        self,
        image_path,
        question,
        temperature=0,
        max_new_tokens=1024,
    ):

        answer = inference_model(
            [image_path],
            question,
            self.model,
            self.tokenizer,
            self.image_processor,
            self.context_len,
            conv_mode="phi",
            temperature=temperature,
            max_new_tokens=max_new_tokens,
        )

        return answer
