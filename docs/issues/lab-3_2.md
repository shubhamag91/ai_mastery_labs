### [Lab-3.2] Merge Weights, Quantize, and Compile GGUF
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 3h
*   **Description:**
    Merge the fine-tuned PEFT adapter weights back into the baseline checkpoint, quantize the unified model, and compile it into GGUF format for CPU/GPU acceleration.

    #### Tasks:
    - [ ] Write a weight merger script to output a unified FP16 baseline model.
    - [ ] Clone `llama.cpp` and build the compilation tools.
    - [ ] Quantize the merged PyTorch weights into INT4 GGUF format (e.g. `q4_k_m`).
    - [ ] Verify model file size compression and load testing.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** What is perplexity? How does quantizing a model from FP16 to INT4 affect the perplexity score and the memory footprint?