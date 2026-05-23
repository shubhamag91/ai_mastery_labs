### [Lab-5.2] Integrate Anthropic Ephemeral Prompt Caching
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 1h
*   **Description:**
    Optimize your extraction pipeline costs and speed by implementing ephemeral Prompt Caching for the static schema and system instructions.

    #### Tasks:
    - [ ] Modify your extraction script to use Anthropic's Messages API.
    - [ ] Inject a large system prompt containing your strict rules and schema definitions.
    - [ ] Add the `"cache_control": {"type": "ephemeral"}` parameter to the static prompt blocks.
    - [ ] Run sequential requests and inspect the token usage metadata to confirm cache hits.

    #### 🎓 Learning Checkpoint:
    - **Destructive Testing:** Send very short requests separated by 10 minutes. Check your cache hit statistics. Study the lifetime of the cache and how pricing scales with call frequency.