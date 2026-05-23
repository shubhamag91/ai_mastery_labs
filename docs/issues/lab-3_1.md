## 🧪 Lab 3: The Deep-Tech Fine-Tuning & Local Inference Sandbox

### [Lab-3.1] Design Dataset and Run QLoRA Training Script
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 4h
*   **Description:**
    Prepare an instruction-tuning dataset and write a training pipeline to fine-tune a small open-source LLM (like Llama-3 8B) locally using QLoRA.

    #### Tasks:
    - [ ] Assemble a custom dataset of 300+ JSON/Markdown examples matching your target output style.
    - [ ] Set up a Python training environment with PyTorch, HuggingFace `transformers`, `peft`, and `trl`.
    - [ ] Write a QLoRA script: load base model in 4-bit, configure LoRA parameters (r, alpha, target modules), and set up the SFTTrainer.
    - [ ] Execute a test training run for 2 epochs, plotting the training loss.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** Why do we quantize the base model to 4-bit before attaching 16-bit LoRA adapter layers? What is the role of the `target_modules` list?
    - **Destructive Testing:** Set an extremely high learning rate (e.g. `1e-1`). Train the model for 1 epoch, observe loss values, and note the signs of gradient explosion.