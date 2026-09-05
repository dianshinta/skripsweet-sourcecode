#!/bin/bash
TRAIN_DATA=/workspace/train.json
VAL_DATA=/workspace/validation.json
TEST_DATA=/workspace/test.json
LLM_PATH=mPLUG/TinyChart-3B-768
VIT_PATH=mPLUG/TinyChart-3B-768-siglip
OUTPUT=/workspace/checkpoints/TinyChart-3B
mkdir -p ${OUTPUT}
cp scripts/train_runpod.sh ${OUTPUT}/
export PYTHONPATH=./
export RANK=0
python \
    tinychart/train/train.py \
    --lora_enable True \
    --lora_r 128 \
    --lora_alpha 256 \
    --lora_dropout 0.05 \
    --tune_vision_tower False \
    --tune_entire_model False \
    --tune_vit_from_layer -1 \
    --model_name_or_path ${LLM_PATH} \
    --vision_tower ${VIT_PATH} \
    --version v1 \
    --data_path ${TRAIN_DATA} \
    --eval_data_path ${VAL_DATA} \
    --image_folder /workspace/tinychart_images \
    --mm_projector_type mlp2x_gelu \
    --mm_vision_select_layer -2 \
    --mm_use_im_start_end False \
    --mm_use_im_patch_token False \
    --image_aspect_ratio pad \
    --group_by_modality_length True \
    --fp16 False \
    --bf16 True \
    --output_dir ${OUTPUT} \
    --num_train_epochs 1 \
    --per_device_train_batch_size 2 \
    --per_device_eval_batch_size 2 \
    --gradient_accumulation_steps 1 \
    --evaluation_strategy "steps" \
    --eval_steps 20000 \
    --save_strategy "steps" \
    --save_steps 20000 \
    --load_best_model_at_end True \
    --metric_for_best_model eval_loss \
    --greater_is_better False \
    --save_total_limit 3 \
    --learning_rate 1e-4 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 50 \
    --tf32 True \
    --model_max_length 1024 \
    --gradient_checkpointing True \
    --dataloader_num_workers 6 \
    --lazy_preprocess True \
    --report_to tensorboard \
2>&1 | tee -a ${OUTPUT}/log.txt
python scripts/convert_model_config.py --input ${OUTPUT}
