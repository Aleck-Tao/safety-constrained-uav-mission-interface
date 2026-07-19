# System Architecture

## 1. Motivation

Autonomous UAV systems require more than a perception module. A practical system must connect sensing, decision logic, communication, action execution and validation. This project explores a UAV architecture in which natural-language mission instructions are translated into structured navigation goals and safety constraints.

## 2. Main Modules

### 2.1 Perception Layer

The perception layer is based on LiDAR and stereo sensing. Its role is to support:

- obstacle awareness,
- local spatial representation,
- trajectory and drift diagnosis,
- environment variation analysis,
- SLAM-style navigation support.

### 2.2 AI-Agent Mission Layer

The AI-agent layer converts a natural-language instruction into a structured plan. The public script in this repository uses a rule-based parser as a transparent demonstration. In future development, this layer can be replaced by or connected to a large language model or VLA-style planning module.

Structured outputs include:

- mission type,
- target area,
- speed preference,
- safety distance,
- return-to-home condition,
- communication-failure behaviour,
- sensor-confidence requirements.

### 2.3 Safety Layer

The safety layer checks whether mission parameters are inside predefined limits. For example:

- minimum obstacle clearance,
- maximum speed,
- valid return-to-home policy,
- communication stability requirement,
- stop condition under low perception confidence.

### 2.4 Communication Layer

Starlink-enabled remote communication is included in the thesis direction as a way to support long-range supervision and remote data transfer. The project treats communication as part of the autonomous-system design rather than as an afterthought.

### 2.5 Validation Layer

Validation is based on:

- trajectory plots,
- timing logs,
- perception-confidence diagnostics,
- failure-mode notes,
- safety-check outputs.

## 3. VLA Research Connection

The project is relevant to Vision-Language-Action models because it implements the same high-level loop:

```text
visual/spatial input + language instruction -> reasoning/planning -> action -> validation
```

This makes the project a practical foundation for future doctoral research on VLA models for autonomous driving or autonomous robotic systems.
