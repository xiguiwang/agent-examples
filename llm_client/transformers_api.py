# Transformers pipline example
from transformers import pipeline
from transformers import TextStreamer

pipe = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct")
messages = [
    {"role": "user", "content": "Who are you?"},
]

data=pipe(messages)
print(data)


# Transformers API example
# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

model="Qwen/Qwen3-8B"
model="/disk/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218"
tokenizer = AutoTokenizer.from_pretrained(model)
model = AutoModelForCausalLM.from_pretrained(model,
    torch_dtype="auto",
    device_map="cuda")

# Initialize a streamer (prints tokens in real-time)
streamer = TextStreamer(
    tokenizer,
    skip_prompt=True,          # Skip the input prompt in output
    skip_special_tokens=True   # Skip special tokens (e.g., </think>)
)

prompt = ["Give me a short introduction to large language model.", "介绍一下中国历史？"]
messages = [
    {"role": "user", "content": prompt[1]},
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=True # Switches between thinking and non-thinking modes. Default is True.
)
model_inputs = tokenizer([text], return_tensors="pt").to("cuda") #model.device)

generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=32768,
    streamer=streamer,          # Enable streaming
    do_sample=True,             # Optional: Enable sampling for diversity
    temperature=0.7,            # Optional: Control randomness
)
output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

# parsing thinking content
try:
    # rindex finding 151668 (</think>)
    index = len(output_ids) - output_ids[::-1].index(151668)
except ValueError:
    index = 0

#thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
#content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

#print(thinking_content)
#print(content)
