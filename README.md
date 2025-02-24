# 🛍️ Online Fashion Shopping Assistant

## 📊 Comparative Conceptual Map
This project integrates multiple tools and frameworks to build a smart e-commerce shopping assistant using **LangChain**, **Hugging Face**, and **SerpAPI**. The system combines:

- **LLM Reasoning with External Tool Use:**
  - Utilizes LangChain to integrate LLMs with external APIs and custom tools.
  - Incorporates a ReAct-style agent for zero-shot reasoning and acting.

- **Custom Tools for E-Commerce:**
  - **E-Commerce Search:** Simulates product searches with filters.
  - **Shipping Estimator:** Estimates shipping costs and delivery times.
  - **Discount Checker:** Checks for available discounts.
  - **Return Policy Checker:** Retrieves store return policies.
  - **SerpAPI Integration:** Conducts real-world product searches when necessary.

## 📈 Short Written Analysis
### Performance & Results:
- **Product Search:** Efficient filtering based on user-defined attributes (color, size, price range).
- **Discount & Shipping:** Accurately applies promotions and estimates shipping feasibility.
- **Fallback Strategy:** Uses SerpAPI to ensure results even when internal search fails.
- **LLM Reasoning:** The Hugging Face model processes complex queries and executes multi-step tasks.

### Observations:
- **Strengths:**
  - Effective multi-tool orchestration.
  - Strong zero-shot capabilities with Hugging Face LLM.
- **Weaknesses:**
  - Occasional misinterpretation of complex queries.
  - Dependency on SerpAPI for real-world searches.

## 🏗️ Design Decisions
### Agent Architecture:
- **LangChain Agents:**
  - Implemented a **ZERO_SHOT_REACT_DESCRIPTION** agent.
  - Uses a **CustomOutputParser** for tailored LLM output interpretation.

- **Tool Integration:**
  - Modular tool design for search, discounts, shipping, and policies.
  - Seamless fallback to SerpAPI for robust product search.

### Tool Selection:
- **LangChain:** For orchestrating LLM and tools.
- **Hugging Face Endpoint:** For text generation tasks.
- **SerpAPI:** For real-time web searches.

## ⚙️ Challenges & Improvements
### Challenges:
- **Query Parsing:**
  - Complex queries occasionally lead to misinterpretations.
- **Fallback Handling:**
  - Managing fallback logic between internal tools and SerpAPI.
- **Error Handling:**
  - Parsing LLM outputs consistently using Regex can be error-prone.

### Improvements:
- **Enhanced Parsing:**
  - Refine **CustomOutputParser** for better action extraction.
- **Dynamic Tool Selection:**
  - Implement adaptive logic to choose tools based on query complexity.
- **Error Resilience:**
  - Improve error handling during fallback operations.

## ❓ Open Questions & References
### Open Questions:
1. How can we improve LLM reasoning to handle ambiguous queries better?
2. What are optimal strategies to balance internal tool use and external API calls?
3. Can we enhance the agent’s reflection mechanism to self-correct mistakes?

### References:
1.Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K. and Cao, Y., 2023, January. React: Synergizing reasoning and acting in language models. In International Conference on Learning Representations (ICLR).

2.Schick, T., Dwivedi-Yu, J., Dessì, R., Raileanu, R., Lomeli, M., Hambro, E., Zettlemoyer, L., Cancedda, N. and Scialom, T., 2023. Toolformer: Language models can teach themselves to use tools. Advances in Neural Information Processing Systems, 36, pp.68539-68551.

3.Aksitov, R., Miryoosefi, S., Li, Z., Li, D., Babayan, S., Kopparapu, K., Fisher, Z., Guo, R., Prakash, S., Srinivasan, P. and Zaheer, M., 2023. Rest meets react: Self-improvement for multi-step reasoning llm agent. arXiv preprint arXiv:2312.10003.

4.Shi, Z., Gao, S., Chen, X., Feng, Y., Yan, L., Shi, H., Yin, D., Chen, Z., Verberne, S. and Ren, Z., 2024. Chain of tools: Large language model is an automatic multi-tool learner. arXiv preprint arXiv:2405.16533.

5.Zhou, A., Yan, K., Shlapentokh-Rothman, M., Wang, H. and Wang, Y.X., 2023. Language agent tree search unifies reasoning acting and planning in language models. arXiv preprint arXiv:2310.04406.
