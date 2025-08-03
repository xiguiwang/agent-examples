from transformers import AutoModelForCausalLM, AutoTokenizer

from transformers import TextStreamer

model_name = "Qwen/Qwen3-0.6B"
#model_name = r"/disk/.cache/huggingface/hub/models--Qwen--Qwen3-4B/snapshots/531c80e289d6cff3a7cd8c0db8110231d23a6f7a"

# load the tokenizer and the model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="cuda"
)

# Initialize a streamer (prints tokens in real-time)
streamer = TextStreamer(
    tokenizer, 
    skip_prompt=True,          # Skip the input prompt in output
    skip_special_tokens=True   # Skip special tokens (e.g., </think>)
)

# prepare the model input
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

# conduct text completion
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=256, #32768,
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

thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

#print("thinking content:", thinking_content)
#print("content:", content)
