# Relevance to Vision-Language-Action Research

Vision-Language-Action (VLA) models aim to connect perception, language understanding and action generation. This UAV project is not an autonomous-driving benchmark, but it is structurally relevant to VLA research.

## 1. Perception

The UAV uses LiDAR/stereo sensing to obtain spatial information about the environment. This corresponds to the visual/spatial input in VLA models.

## 2. Language

The AI-agent layer accepts natural-language mission commands. Examples include obstacle clearance, target area, return behaviour and safety constraints.

## 3. Action

The structured mission plan can be converted into navigation objectives, safety policies and stop/return decisions.

## 4. Safety and Generalization

The project emphasizes safety-aware execution and failure diagnosis. This connects to key research questions in VLA autonomous driving, including:

- robustness to rare or novel situations,
- long-horizon task reasoning,
- safe action execution,
- interpretable failure analysis,
- efficient inference for real deployment.

## 5. Future Extensions

Possible extensions include:

- connecting the parser to an LLM/VLM/VLA model,
- adding camera-image captions for mission awareness,
- integrating LiDAR-camera fusion,
- using CARLA or another simulator for driving-style VLA experiments,
- evaluating failure cases under communication loss or low sensor confidence.
