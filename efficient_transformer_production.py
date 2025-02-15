# -*- coding: utf-8 -*-
"""efficient transformer production.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/17AsY4IQEPbM0762cTMSPLmcHoDxuQpkK
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from transformers import pipeline

bert_ckpt = "transformersbook/bert-base-uncased-finetuned-clinc"
pipe = pipeline("text-classification", model=bert_ckpt)

query = """Hey, I'd like to rent a vehicle from Nov 1st to Nov 15th in
Paris and I need a 15 passenger van"""
pipe(query)

class PerformanceBenchmark:
  def __init__(self, pipeline, dataset, optim_type="BERT baseline"):
    self.pipeline = pipeline
    self.dataset = dataset
    self.optim_type = optim_type

  def compute_accuracy(self):
  # We'll define this later
    pass

  def compute_size(self):
  # We'll define this later
    pass

  def time_pipeline(self):
  # We'll define this later
    pass

  def run_benchmark(self):
    metrics = {}
    metrics[self.optim_type] = self.compute_size()
    metrics[self.optim_type].update(self.time_pipeline())
    metrics[self.optim_type].update(self.compute_accuracy())
    return metrics

!pip install datasets
import datasets

from datasets import load_dataset

clinc = load_dataset('clinc_oos', "plus")

sample = clinc["test"][42]
sample

intents = clinc["test"].features["intent"]
intents.int2str(sample["intent"])

!pip install evaluate

from evaluate import load

accuracy_score = load("accuracy")

def compute_accuracy(self):
  """This overrides the PerformanceBenchmark.compute_accuracy() method"""
  preds, labels = [], []
  for example in self.dataset:
    pred = self.pipeline(example["text"])[0]["label"]
    label = example["intent"]
    preds.append(intents.str2int(pred))
    labels.append(label)
  accuracy = accuracy_score.compute(predictions=preds, references=labels)
  print(f"Accuracy on test set - {accuracy['accuracy']:.3f}")
  return accuracy

PerformanceBenchmark.compute_accuracy = compute_accuracy

import torch

torch.save(pipe.model.state_dict(), "model.pt")

from pathlib import Path

def compute_size(self):
  """This overrides the PerformanceBenchmark.compute_size() method"""
  state_dict = self.pipeline.model.state_dict()
  tmp_path = Path("model.pt")
  torch.save(state_dict, tmp_path)
  # Calculate size in megabytes
  size_mb = Path(tmp_path).stat().st_size / (1024 * 1024)
  # Delete temporary file
  tmp_path.unlink()
  print(f"Model size (MB) - {size_mb:.2f}")
  return {"size_mb": size_mb}

PerformanceBenchmark.compute_size = compute_size

from time import perf_counter

for _ in range(3):
 start_time = perf_counter()
 _ = pipe(query)
 latency = perf_counter() - start_time
 print(f"Latency (ms) - {1000 * latency:.3f}")

import numpy as np

def time_pipeline(self, query="What is the pin number for my account?"):
  """This overrides the PerformanceBenchmark.time_pipeline() method"""
  latencies = []
  # Warmup
  for _ in range(10):
    _ = self.pipeline(query)
  # Timed run
  for _ in range(100):
    start_time = perf_counter()
    _ = self.pipeline(query)
    latency = perf_counter() - start_time
    latencies.append(latency)
  # Compute run statistics
  time_avg_ms = 1000 * np.mean(latencies)
  time_std_ms = 1000 * np.std(latencies)
  print(f"Average latency (ms) - {time_avg_ms:.2f} +\- {time_std_ms:.2f}")
  return {"time_avg_ms": time_avg_ms, "time_std_ms": time_std_ms}

PerformanceBenchmark.time_pipeline = time_pipeline

pb = PerformanceBenchmark(pipe, clinc["test"])
perf_metrics = pb.run_benchmark()

from transformers import TrainingArguments

class DistillationTrainingArguments(TrainingArguments):
  def __init__(self, *args, alpha=0.5, temperature=2.0, **kwargs):
    super().__init__(*args, **kwargs)
    self.alpha = alpha
    self.temperature = temperature

import torch.nn as nn
import torch.nn.functional as F
from transformers import Trainer

class DistillationTrainer(Trainer):
  def __init__(self, *args, teacher_model=None, **kwargs):
    super().__init__(*args, **kwargs)
    self.teacher_model = teacher_model

  def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None): # Add num_items_in_batch argument
    outputs_stu = model(**inputs)
    # Extract cross-entropy loss and logits from student
    loss_ce = outputs_stu.loss
    logits_stu = outputs_stu.logits
    # Extract logits from teacher
    with torch.no_grad():
      outputs_tea = self.teacher_model(**inputs)
      logits_tea = outputs_tea.logits

    # Soften probabilities and compute distillation loss
    loss_fct = nn.KLDivLoss(reduction="batchmean")
    loss_kd = self.args.temperature ** 2 * loss_fct(
    F.log_softmax(logits_stu / self.args.temperature, dim=-1),
    F.softmax(logits_tea / self.args.temperature, dim=-1))
    # Return weighted student loss
    loss = self.args.alpha * loss_ce + (1. - self.args.alpha) * loss_kd
    return (loss, outputs_stu) if return_outputs else loss

from transformers import AutoTokenizer
student_ckpt = "distilbert-base-uncased"
student_tokenizer = AutoTokenizer.from_pretrained(student_ckpt)
def tokenize_text(batch):
 return student_tokenizer(batch["text"], truncation=True)
clinc_enc = clinc.map(tokenize_text, batched=True, remove_columns=["text"])
clinc_enc = clinc_enc.rename_column("intent", "labels")

from huggingface_hub import notebook_login
notebook_login()

def compute_metrics(pred):
 predictions, labels = pred
 predictions = np.argmax(predictions, axis=1)
 return accuracy_score.compute(predictions=predictions, references=labels)

batch_size = 48
finetuned_ckpt = "distilbert-base-uncased-finetuned-clinc"
student_training_args = DistillationTrainingArguments(
 output_dir=finetuned_ckpt, evaluation_strategy = "epoch",
 num_train_epochs=5, learning_rate=2e-5,
 per_device_train_batch_size=batch_size,
 per_device_eval_batch_size=batch_size, alpha=1, weight_decay=0.01,
 push_to_hub=False, report_to='none')

id2label = pipe.model.config.id2label
label2id = pipe.model.config.label2id

from transformers import AutoConfig
num_labels = intents.num_classes
student_config = (AutoConfig
 .from_pretrained(student_ckpt, num_labels=num_labels,
 id2label=id2label, label2id=label2id))

import torch
from transformers import AutoModelForSequenceClassification

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def student_init():
  return (AutoModelForSequenceClassification
  .from_pretrained(student_ckpt, config=student_config).to(device))

teacher_ckpt = "transformersbook/bert-base-uncased-finetuned-clinc"
teacher_model = (AutoModelForSequenceClassification
 .from_pretrained(teacher_ckpt, num_labels=num_labels)
 .to(device))
distilbert_trainer = DistillationTrainer(model_init=student_init,
 teacher_model=teacher_model, args=student_training_args,
 train_dataset=clinc_enc['train'], eval_dataset=clinc_enc['validation'],
 compute_metrics=compute_metrics, tokenizer=student_tokenizer)
distilbert_trainer.train()

distilbert_trainer.push_to_hub("Training completed!")

finetuned_ckpt = "navidfalah/distilbert-base-uncased-finetuned-clinc"
pipe = pipeline("text-classification", model=finetuned_ckpt)

optim_type = "DistilBERT"
pb = PerformanceBenchmark(pipe, clinc["test"], optim_type=optim_type)
perf_metrics.update(pb.run_benchmark())

perf_metrics

import pandas as pd

def plot_metrics(perf_metrics, current_optim_type):
  df = pd.DataFrame.from_dict(perf_metrics, orient='index')

  for idx in df.index:
    df_opt = df.loc[idx]
    # Add a dashed circle around the current optimization type
    if idx == current_optim_type:
      plt.scatter(df_opt["time_avg_ms"], df_opt["accuracy"] * 100,
      alpha=0.5, s=df_opt["size_mb"], label=idx,
      marker='$\u25CC$')
    else:
      plt.scatter(df_opt["time_avg_ms"], df_opt["accuracy"] * 100,
      s=df_opt["size_mb"], label=idx, alpha=0.5)

  legend = plt.legend(bbox_to_anchor=(1,1))

  plt.ylim(80,90)
  # Use the slowest model to define the x-axis range
  xlim = int(perf_metrics["BERT baseline"]["time_avg_ms"] + 3)
  plt.xlim(1, xlim)
  plt.ylabel("Accuracy (%)")
  plt.xlabel("Average latency (ms)")
  plt.show()

plot_metrics(perf_metrics, optim_type)

def objective(trial):
 x = trial.suggest_float("x", -2, 2)
 y = trial.suggest_float("y", -2, 2)
 return (1 - x) ** 2 + 100 * (y - x ** 2) ** 2

!pip install optuna

import optuna
study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=100)

study.best_params

def hp_space(trial):
 return {"num_train_epochs": trial.suggest_int("num_train_epochs", 5, 10),
 "alpha": trial.suggest_float("alpha", 0, 1),
 "temperature": trial.suggest_int("temperature", 2, 20)}

best_run = distilbert_trainer.hyperparameter_search(n_trials=20, direction="maximize", hp_space=hp_space)

print(best_run)

for k,v in best_run.hyperparameters.items():
 setattr(student_training_args, k, v)
# Define a new repository to store our distilled model
distilled_ckpt = "distilbert-base-uncased-distilled-clinc"
student_training_args.output_dir = distilled_ckpt
# Create a new Trainer with optimal parameters
distil_trainer = DistillationTrainer(model_init=student_init,
 teacher_model=teacher_model, args=student_training_args,
 train_dataset=clinc_enc['train'], eval_dataset=clinc_enc['validation'],
 compute_metrics=compute_metrics, tokenizer=student_tokenizer)
distil_trainer.train();

distil_trainer.push_to_hub("Training complete")

distilled_ckpt = "transformersbook/distilbert-base-uncased-distilled-clinc"
pipe = pipeline("text-classification", model=distilled_ckpt)
optim_type = "Distillation"
pb = PerformanceBenchmark(pipe, clinc["test"], optim_type=optim_type)
perf_metrics.update(pb.run_benchmark())

plot_metrics(perf_metrics, optim_type)

import matplotlib.pyplot as plt
import torch  # Ensure PyTorch is imported

# Assuming 'pipe.model.state_dict()' is a valid way to access the model state dictionary
state_dict = pipe.model.state_dict()

# Extract the weights of a specific layer
weights = state_dict["distilbert.transformer.layer.0.attention.out_lin.weight"]

# Plot the histogram of the flattened weights
plt.hist(weights.cpu().numpy().flatten(), bins=250, range=(-0.3, 0.3), edgecolor="C0")
plt.xlabel("Weight values")
plt.ylabel("Frequency")
plt.title("Histogram of Attention Layer Weights")
plt.show()

zero_point = 0
scale = (weights.max() - weights.min()) / (127 - (-128))

(weights / scale + zero_point).clamp(-128, 127).round().char()

from torch import quantize_per_tensor
dtype = torch.qint8
quantized_weights = quantize_per_tensor(weights, scale, zero_point, dtype)
quantized_weights.int_repr()

# Commented out IPython magic to ensure Python compatibility.
# %%timeit
# weights @ weights

from torch.nn.quantized import QFunctional
q_fn = QFunctional()

from torch.quantization import quantize_dynamic
model_ckpt = "transformersbook/distilbert-base-uncased-distilled-clinc"
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
model = (AutoModelForSequenceClassification
 .from_pretrained(model_ckpt).to("cpu"))
model_quantized = quantize_dynamic(model, {nn.Linear}, dtype=torch.qint8)

pipe = pipeline("text-classification", model=model_quantized,
 tokenizer=tokenizer)
optim_type = "Distillation + quantization"
pb = PerformanceBenchmark(pipe, clinc["test"], optim_type=optim_type)
perf_metrics.update(pb.run_benchmark())

plot_metrics(perf_metrics, optim_type)

from torch.quantization import quantize_dynamic

model_ckpt = "transformersbook/distilbert-base-uncased-distilled-clinc"
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
model = (AutoModelForSequenceClassification
 .from_pretrained(model_ckpt).to("cpu"))
model_quantized = quantize_dynamic(model, {nn.Linear}, dtype=torch.qint8)

pipe = pipeline("text-classification", model=model_quantized,
 tokenizer=tokenizer)
optim_type = "Distillation + quantization"
pb = PerformanceBenchmark(pipe, clinc["test"], optim_type=optim_type)
perf_metrics.update(pb.run_benchmark())

plot_metrics(perf_metrics, optim_type)

import os
from psutil import cpu_count
os.environ["OMP_NUM_THREADS"] = f"{cpu_count()}"
os.environ["OMP_WAIT_POLICY"] = "ACTIVE"

from transformers.convert_graph_to_onnx import convert
model_ckpt = "transformersbook/distilbert-base-uncased-distilled-clinc"
onnx_model_path = Path("onnx/model.onnx")
convert(framework="pt", model=model_ckpt, tokenizer=tokenizer,
 output=onnx_model_path, opset=12, pipeline_name="text-classification")

