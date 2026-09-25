# ADR 0009: Category strategies

Status: accepted

## Decision
0.3.0 supports `single` and `directories` category strategies. `single` preserves 0.2.x output. `directories` maps source parent directories below the scan root to nested ToolHub LOCAL categories. Tool names continue to come from ToolSpec `name`.
