import torch
import os
from peft import PeftModel
from transformers import AutoTokenizer

from tinychart.model.builder import load_pretrained_model
from tinychart.mm_utils import get_model_name_from_path
from tinychart.eval.run_tiny_chart import inference_model
from tinychart.eval.eval_metric import parse_model_output, evaluate_cmds


class TinyChartInference:

    def __init__(
        self,
        base_model="mPLUG/TinyChart-3B-768",
        lora_model="shiinn97/tinychart3B-indochartqa",
        hf_token=os.getenv("HF_TOKEN"),
        device=None,
    ):

        self.base_model = base_model
        self.lora_model = lora_model
        self.device = device or (
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        print("=" * 60)
        print("Loading TinyChart...")
        print("=" * 60)

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.lora_model,
            token=""
        )

        _, model, image_processor, context_len = load_pretrained_model(
            self.base_model,
            model_base=None,
            model_name=get_model_name_from_path(self.base_model),
            device=self.device,
        )

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

        # ==========================================
        # 1. Generate PoT dari model
        # ==========================================
        pot_output = inference_model(
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

        cmds = parse_model_output(pot_output)

        try:
            answer = evaluate_cmds(cmds)

        except Exception as e:
            print("\nPoT EVALUATION ERROR:")
            print(e)

            answer = None

        return {
            "pot": pot_output,
            "answer": str(answer) if answer is not None else None
        }
