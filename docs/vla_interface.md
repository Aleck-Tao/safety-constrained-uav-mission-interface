# VLA / Learned-Agent Integration Boundary

A learned language or Vision-Language-Action component can replace the public constrained-language parser, but it must emit the same versioned contract and cannot override gate decisions.

Recommended integration sequence:

1. perception and operator language are processed by the learned component;
2. the component proposes a mission contract plus confidence and provenance;
3. schema validation rejects malformed output;
4. deterministic policy validation rejects missing or unsafe constraints;
5. accepted contracts are combined with live navigation state by a separate adapter;
6. execution and gate decisions are logged for post-flight analysis.

This design does not make the public parser a VLA model. It creates an auditable interface for comparing rule-based, LLM-based, and future multimodal parsers under the same downstream safety constraints.
