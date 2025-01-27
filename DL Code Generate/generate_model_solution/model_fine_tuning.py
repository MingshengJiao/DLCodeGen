
import os
import json
import argparse
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config, DataCollatorForLanguageModeling, Trainer, TrainingArguments,TextDataset


def main():
    model_repository_path = "/mnt/sda/HuggingfaceRepositories/models/"
    model_path = model_repository_path + "gpt2-large"

    train_data_path = "/mnt/sda/Kaggle/gpt2-large-ft/train_dir/train_1216_tokened.txt"
    eval_data_path = "/mnt/sda/Kaggle/gpt2-large-ft/train_dir/eval_1216_tokened.txt"

    store_model_path = "/mnt/sda/Kaggle/gpt2-large-ft/1216_tokened/model_checkpoint"
    logging_dir_path="/mnt/sda/Kaggle/gpt2-large-ft/1216_tokened/logs"
    final_model_path = "/mnt/sda/Kaggle/gpt2-large-ft/1216_tokened/model"
    os.makedirs(store_model_path, exist_ok=True)
    os.makedirs(logging_dir_path, exist_ok=True)
    os.makedirs(final_model_path, exist_ok=True)

    device = "cuda"
    tokenizer = GPT2Tokenizer.from_pretrained(model_path)
    tokenizer.padding_side = "left"
    tokenizer.pad_token = tokenizer.eos_token # to avoid an error   
    tokenizer.add_special_tokens({'sep_token':"<|sep|>"})

    model = GPT2LMHeadModel.from_pretrained(model_path, pad_token_id=tokenizer.eos_token_id, device_map="auto")
    model.resize_token_embeddings(len(tokenizer))
    train_dataset = TextDataset(
        tokenizer=tokenizer, 
        file_path=train_data_path, 
        block_size=1024
    )

    eval_dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=eval_data_path,
        block_size=1024
    )
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_args = TrainingArguments(
        output_dir=store_model_path,      # 模型和训练日志的输出目录
        logging_dir=logging_dir_path,             # 日志输出目录
        overwrite_output_dir=True,        # 是否覆盖输出目录

        logging_strategy="epoch",         # 日志记录策略，在每个epoch后
        save_strategy="epoch",
        save_total_limit=3,
        evaluation_strategy="epoch",       # 每个epoch进行评估
        load_best_model_at_end=True,       # 加载评估结果最好的模型
        metric_for_best_model="eval_loss", # 依据评估的损失（loss）选择最好的模型
        greater_is_better=False,           # eval_loss越小越好

        num_train_epochs = 6,
        per_device_train_batch_size=1,    # 每个设备上的训练 batch size
        gradient_accumulation_steps=8,
        dataloader_drop_last=False,        # 是否丢弃最后一个不完整的 batch
        run_name="gpt2-large-1216-tokened",       # 训练运行的名称

        learning_rate=1e-3,               # 初始学习率
        lr_scheduler_type="cosine",
        weight_decay=0.01,
        warmup_steps=100,               # 学习率 warmup 步数
    )

    trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator)

    trainer.train()
    model.save_pretrained(final_model_path)
    tokenizer.save_pretrained(final_model_path)  # 保存分词器

if __name__ == "__main__":
    main()