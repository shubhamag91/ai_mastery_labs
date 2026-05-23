### [Lab-2.3] Integrate MongoDB Persistence & Graph Recovery
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 3h
*   **Description:**
    Connect MongoDB as the persistent storage engine for your stateful graph, enabling state resumption, history tracking, and process recovery.

    #### Tasks:
    - [ ] Add a `mongodb` service to your `docker-compose.yml` configuration.
    - [ ] Implement a custom Langgraph `Saver` or checkpoint database class backed by MongoDB.
    - [ ] Store session history, agent states, and prompt configurations dynamically in collections.
    - [ ] Test "Time Travel": write a script that queries historical states in Mongo and rolls back the graph state to an earlier execution turn.

    #### 🎓 Learning Checkpoint:
    - **Destructive Testing:** Run a complex 3-step agent run. In the middle of step 2, forcibly kill the Python process. Write a recovery script that fetches the last state from MongoDB and resumes the agent cleanly.