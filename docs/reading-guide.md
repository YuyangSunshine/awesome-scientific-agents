# Reading guide

[← Home](../README.md) · [Taxonomy](taxonomy.md)

This route is an editorial starting point, not a quality ranking. Use the stable IDs to find entries in the topic lists or dataset. Read the source and its limitations before making a capability claim.

## 1. Establish the landscape

Start with **M0001**, *Scientific discovery in the age of artificial intelligence*, and **M0002**, *From Automation to Autonomy*. For the laboratory perspective, use **M0023**, *Self-Driving Laboratories for Chemistry and Materials Science*. Inspect their coverage before treating a newer framework as novel. [Survey list](../papers/surveys.md).

## 2. Compare concrete scientific systems

Read **M0015** (Virtual Lab), **M0011** (Co-Scientist), **M0016** (Robin), and **M0021** (published AI Scientist study) in the [scientific agents list](../papers/scientific-agents.md). Compare the scientific task, researcher intervention, experimental environment, and acceptance of conclusions. Related AI Scientist preprints **M0009** and **M0010** retain separate IDs; their claims should not be silently replaced by those of the later article.

For physical experimentation, read **M0026** (A-Lab) **together with M0027, its correction**, then browse [autonomous laboratories](../papers/autonomous-labs.md). Separate synthesis, identification, and novelty when reading material-discovery claims.

## 3. Trace a result to a scientific claim

Browse [scientific reasoning and evidence](../papers/scientific-evidence.md). For each system, ask what was measured, which claim that measurement supports, what alternative explanations remain, and whether the same claim received an independent test. A working experiment, a generated paper, and a supported mechanistic explanation are different endpoints.

## 4. Ask what changes through learning

Use **M0053**, *Active learning-assisted directed evolution*, as a concrete experiment-design case, then explore [active learning](../papers/experiment-design.md) and [continual learning](../papers/continual-learning.md). Separate optimization within one study from gains on later tasks. Record the updated object, time scale, frozen-versus-updated comparison, budget, and transfer test. Background learning methods in this collection do not automatically constitute scientific-agent evidence.

## 5. Interpret evaluation in context

Browse [benchmarks](../papers/benchmarks.md), including ScienceAgentBench, ChemBench and PaperBench. Identify the evaluated task and unit, available tools, intervention, scoring rule, and relationship between a score and a scientific claim. Compare results only when the constructs and conditions support the comparison.

## A compact reading-note template

```text
Paper ID and source version:
Task / domain / execution environment:
Researcher control and system decisions:
Claim and measured endpoint:
Supporting source location:
Independent validation reported by the paper:
Learning object / time scale / comparison:
Interpretation limits and unresolved questions:
```

Mark missing information as unreported or pending inspection. A completed reading note is distinct from an independent reproduction.
