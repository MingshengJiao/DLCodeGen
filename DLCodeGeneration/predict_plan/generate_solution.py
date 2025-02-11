from transformers import GPT2Tokenizer, GPT2Model, GPT2LMHeadModel, pipeline

model_repository_path = "/mnt/sda/Kaggle/gpt2-large-ft/"
model_path = model_repository_path + "1216_tokened/model_checkpoint/checkpoint-233/"

device = "cuda"

tokenizer = GPT2Tokenizer.from_pretrained("/mnt/sda/Kaggle/gpt2-large-ft/1216_tokened/model")

model = GPT2LMHeadModel.from_pretrained(model_path, pad_token_id=tokenizer.eos_token_id, device_map="auto")
# so the padding should be on the left
tokenizer.padding_side = "left" 
tokenizer.pad_token = tokenizer.eos_token # to avoid an error

print(tokenizer.vocab_size)
print(tokenizer.model_max_length)
print(tokenizer.model_input_names)

test_question_path = model_repository_path + "train_dir/test_1216_tokened.txt"
predict_path = model_path + "large1216_beam_tokened_233.txt"

lines = []
ans_lines = []
with open(test_question_path, "r") as f:
    lines = f.readlines()
lines = [line.replace('\n', '') for line in lines]
count = 0


inputs = tokenizer(lines, return_tensors="pt", padding=True).to(device)

batch_size = 8
batch_greedy_outputs = []
for_range = int((len(lines)+7)/batch_size + 1)

# ----- batch generate
for i in range(1, for_range):
    start = (i-1)*batch_size
    end = i*batch_size if i*batch_size <= len(lines) else len(lines)

    # greedy decoding
    # batch_greedy_output = model.generate(input_ids=inputs['input_ids'][start:end], attention_mask=inputs['attention_mask'][start:end], max_length=1000)
    
    # beam decoding with beam 5
    batch_greedy_output = model.generate(input_ids=inputs['input_ids'][start:end], attention_mask=inputs['attention_mask'][start:end], max_length=700, num_beams=3, num_return_sequences=1)

    batch_greedy_outputs += batch_greedy_output

ans_lines = []
for i, output in enumerate(batch_greedy_outputs):
    print(f"{i}: {lines[i]}")
    gt = tokenizer.decode(output, skip_special_tokens=True)
    print(gt.replace('\n', '') + '\n')
    ans_lines.append(gt.replace('\n', '') + '\n')
    
with open(predict_path, "w") as f1:
    f1.writelines(ans_lines)
