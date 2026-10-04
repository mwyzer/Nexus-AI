# 10 — Evaluation Specification

## Overview

Nexus AI includes a comprehensive evaluation framework for measuring and improving RAG and Agent performance. Evaluations run as background jobs and results are stored for comparison.

## RAG Evaluation

### Metrics

```python
class RAGEvalMetrics(BaseModel):
    faithfulness: float      # 0-1: Is answer grounded in context?
    answer_relevance: float  # 0-1: Does answer address the question?
    context_precision: float # 0-1: Are retrieved chunks relevant?
    context_recall: float    # 0-1: Were all relevant chunks retrieved?
    ndcg: float              # Normalized Discounted Cumulative Gain
```

### Evaluation Dataset

```python
class RAGEvalDataset(BaseModel):
    id: UUID
    name: str
    knowledge_base_id: UUID
    entries: list[RAGEvalEntry]

class RAGEvalEntry(BaseModel):
    question: str
    ground_truth_answer: str
    relevant_chunk_ids: list[UUID]  # Known relevant chunks
```

### Evaluation Pipeline

```python
async def evaluate_rag(
    dataset: RAGEvalDataset,
    rag_pipeline: RAGPipeline,
) -> RAGEvalResult:
    results = []
    for entry in dataset.entries:
        # 1. Run RAG pipeline
        response = await rag_pipeline.query(entry.question)
        
        # 2. Calculate metrics
        faithfulness = await eval_faithfulness(response.answer, response.citations)
        relevance = await eval_answer_relevance(entry.question, response.answer)
        precision = eval_context_precision(response.citations, entry.relevant_chunk_ids)
        recall = eval_context_recall(response.citations, entry.relevant_chunk_ids)
        
        results.append(RAGEvalMetrics(
            faithfulness=faithfulness,
            answer_relevance=relevance,
            context_precision=precision,
            context_recall=recall,
        ))
    
    return aggregate_results(results)
```

### Faithfulness Evaluation

Uses LLM-as-judge pattern:

```
You are evaluating the faithfulness of an AI-generated answer.

Context: {context}
Answer: {answer}

Rate whether EVERY claim in the answer is supported by the context.
Respond with:
- Score: 0-5 (5 = fully faithful)
- Explanation: brief justification
- Hallucinated claims: list any unsupported claims
```

## Agent Evaluation

### Metrics

```python
class AgentEvalMetrics(BaseModel):
    task_completion: float      # 0-1: Did agent complete the task?
    tool_accuracy: float        # 0-1: Were tools called correctly?
    efficiency: float           # Steps used / optimal steps
    output_quality: float       # 0-5: Human eval of output
    error_recovery: float       # 0-1: Recovered from errors?
    latency_ms: float           # Total execution time
```

### Evaluation Dataset

```python
class AgentEvalDataset(BaseModel):
    id: UUID
    name: str
    entries: list[AgentEvalEntry]

class AgentEvalEntry(BaseModel):
    task: str
    expected_output: str
    expected_tools: list[str]   # Tools expected to be used
    min_steps: int              # Minimum reasonable steps
    max_steps: int              # Maximum allowed steps
```

### Evaluation Pipeline

```python
async def evaluate_agent(
    dataset: AgentEvalDataset,
    agent: Agent,
    n_runs: int = 3,
) -> AgentEvalResult:
    results = []
    for entry in dataset.entries:
        run_results = []
        for _ in range(n_runs):
            output = await agent.run(entry.task)
            run_results.append(eval_single_run(output, entry))
        results.append(aggregate_runs(run_results))
    return aggregate_results(results)
```

## A/B Testing

```python
class ABTest(BaseModel):
    id: UUID
    name: str
    variant_a: ABTestVariant  # Control
    variant_b: ABTestVariant  # Treatment
    traffic_split: float = 0.5
    metric: str  # Primary metric to compare
    duration_days: int = 7

class ABTestVariant(BaseModel):
    description: str
    config: dict[str, Any]  # e.g., different chunk size, model, prompt
```

## Dashboard Metrics

| Section       | Metrics Shown                                |
|---------------|----------------------------------------------|
| Overview      | Overall scores, trends, pass/fail rates       |
| RAG           | Faithfulness, relevance, precision, recall    |
| Agent         | Completion rate, tool accuracy, latency       |
| Comparisons   | Side-by-side A/B test results                 |
| Alerts        | Score drops below threshold                   |

## Scheduled Evaluations

Evaluations run:
- **On-demand** — manual trigger
- **Scheduled** — daily/weekly cron
- **On-change** — when KB or agent config changes
- **CI/CD gate** — block deployment if scores drop
