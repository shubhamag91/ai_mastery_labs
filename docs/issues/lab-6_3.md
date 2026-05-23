### [Lab-6.3] Define Sequenced Research & Analysis Tasks with Search Tools
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Equip your Research Agent with a search tool (like Serper or Brave Search) and define the sequenced tasks that they must perform.

    #### Tasks:
    - [ ] Register a free search API key (Serper or Brave).
    - [ ] Create search tools and assign them exclusively to the Research Agent.
    - [ ] Define the `Research Task` (gather raw competitor data) and the `Analysis Task` (compile comparative matrices).
    - [ ] Link the tasks together, ensuring that the second task uses the output of the first as its input.

    #### 🎓 Learning Checkpoint:
    - **Destructive Testing:** Revoke the search tool key or supply a faulty search API response. Run the crew and observe how the Research Agent attempts to recover or fail gracefully.