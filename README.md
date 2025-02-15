# 🐍 Efficient Transformer Production

## 📝 Description
This Python script demonstrates how to optimize and deploy transformer models for efficient production use. It covers techniques like **knowledge distillation**, **quantization**, and **ONNX conversion** to improve model performance, reduce latency, and minimize memory usage. The script uses the `transformers` library and benchmarks the performance of different optimization strategies. 🛠️

---

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/navidfalah/efficient-transformer-production.git
   cd efficient-transformer-production
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install additional libraries:
   ```bash
   pip install datasets evaluate optuna nlpaug
   ```

---

## 🚀 Usage

1. Run the script:
   ```bash
   python efficient_transformer_production.py
   ```

2. The script will:
   - Load a pre-trained BERT model fine-tuned on the CLINC dataset.
   - Perform knowledge distillation to train a smaller DistilBERT model.
   - Apply quantization to reduce model size and improve inference speed.
   - Convert the model to ONNX format for deployment.
   - Benchmark the performance of each optimization step.

---

## 📂 File Structure

```
efficient-transformer-production/
├── efficient_transformer_production.py  # Main script
├── README.md                            # This file
├── requirements.txt                     # Dependencies
└── onnx/                                # ONNX model output
```

---

## 🧩 Key Features

- **Knowledge Distillation**:
  - Train a smaller DistilBERT model using a larger BERT model as a teacher.
  - Optimize hyperparameters using Optuna for better performance.

- **Quantization**:
  - Apply dynamic quantization to reduce model size and improve inference speed.
  - Compare performance metrics (accuracy, latency, size) before and after quantization.

- **ONNX Conversion**:
  - Convert the PyTorch model to ONNX format for efficient deployment.

- **Performance Benchmarking**:
  - Measure model accuracy, latency, and size for each optimization step.
  - Visualize performance metrics using matplotlib.

---

## 📊 Example Outputs

1. **Performance Metrics**:
   - Accuracy, latency, and model size for each optimization step.
   - Comparison of BERT baseline, DistilBERT, and quantized models.

2. **Visualizations**:
   - Scatter plots comparing accuracy vs. latency for different models.
   - Histograms of model weights before and after quantization.

---

## 🤖 Models Used

- **BERT Baseline**: A fine-tuned BERT model for text classification.
- **DistilBERT**: A smaller, distilled version of BERT trained using knowledge distillation.
- **Quantized DistilBERT**: A quantized version of DistilBERT for efficient inference.
- **ONNX Model**: A DistilBERT model converted to ONNX format for deployment.

---

## 📈 Performance Metrics

- **Accuracy**: Classification accuracy on the CLINC dataset.
- **Latency**: Average inference time in milliseconds.
- **Model Size**: Size of the model in megabytes.

---

## 🛠️ Dependencies

- Python 3.x
- Libraries:
  - `transformers`, `datasets`, `evaluate`
  - `torch`, `optuna`, `nlpaug`
  - `matplotlib`, `pandas`, `numpy`

---

## 🤝 Contributing

Contributions are welcome! 🎉 Feel free to open an issue or submit a pull request.

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m "Add your feature"`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Open a pull request.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Hugging Face for the `transformers` library.
- Optuna for hyperparameter optimization.
- ONNX for model conversion and deployment.

---

## 👤 Author

- **Name**: Navid Falah
- **GitHub**: [navidfalah](https://github.com/navidfalah)
- **Email**: navid.falah7@gmail.com
