# **Evaluation Metrics**

Execution Accuracy will be used to evaluate the accuracy of the fine-tuned SLM, using the _chinook_ database as the test environment. Execution Accuracy measures the percentage of generated SQL queries that produce the correct results when executed against the database.

---

60 questions of different diffculties will be used for evaluation. The result of the fine-tuned SLM will be compared against the results of a baseline SLM that has not been fine-tuned. The baseline SLM will also be evaluated using Execution Accuracy on the same set of questions.
