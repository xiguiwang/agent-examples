# Transformers pipline example
from transformers import pipeline
pipe = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct")
messages = [
    {"role": "user", "content": "Who are you?"},
]

data=pipe(messages)
print(data)


# Transformers API example
# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

#model="Qwen/Qwen2.5-0.5B-Instruct"
model="/media/xwang/E/models--Qwen--Qwen3-0.6B/snapshots/e6de91484c29aa9480d55605af694f39b081c455"
tokenizer = AutoTokenizer.from_pretrained(model)
model = AutoModelForCausalLM.from_pretrained(model)

