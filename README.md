# Multi Agent Hackathon Code Repository

Welcome to our code repository for the [Multi Agent Hackathon](https://alignmentjam.com/jam/multiagent)! This hackathon focused on discovery the failure in the multi-agent systems. Our team worked on **Scaling Laws of LLM Cooperation**, and this repository provides an in-depth look at our code and results.

Our exploration answer a interesting question that, will the failure cases exacerbate as the number of agents increases? 
To demonstrate this, we let LLMs play the **n-player Prisoner‘s Dilemma**, our results demonstrate that the LLM agents experienced **unintended failure as the scale of agents increased**. 



## Installation

   ```shell
   git clone git@github.com:ReedZyd/MultiAgentHackathon.git
   cd MultiAgentHackathon
   pip install -r requirements.txt

   ```
## Reproduce Results

1. To run single-round game:
  ```shell
  python test_nPrisoners.py
  ```
2. To run multiple-round game:
  ```shell
  python test_nPrisoners.py --repeated-game
  ```
3. To use ChatGPT API 'gpt-4', please add `--gpt gpt-4`