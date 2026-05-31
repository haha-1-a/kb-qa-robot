from typing import List, Optional

from openai import OpenAI

from config import Config

SYSTEM_PROMPT = """你是一个专业的企业知识库问答助手。你的任务是基于提供的参考资料回答用户问题。

规则：
1. 只根据参考资料回答，不要编造信息
2. 如果参考资料中没有相关信息，回答"抱歉，知识库中暂无相关内容"
3. 回答要简洁、准确、专业
4. 引用来源时标注文件名"""


def build_prompt(query: str, contexts) -> str:
    """contexts: [(text, metadata, score), ...]"""
    context_text = "\n\n".join([
        f"[来源：{meta.get('source', 'unknown')} 相关度：{score:.2f}]\n{text}"
        for text, meta, score in contexts
    ])

    return f"""参考资料：
{context_text}

问题：{query}

请给出回答："""


class DeepSeekClient:
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = None,
    ):
        self.api_key = api_key or Config.DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("未设置 DEEPSEEK_API_KEY")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=Config.DEEPSEEK_BASE_URL,
        )
        self.model = model or Config.DEFAULT_MODEL
        self.temperature = temperature if temperature is not None else Config.DEFAULT_TEMPERATURE

    def chat(self, messages: List[dict]) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return resp.choices[0].message.content

    def answer_with_context(
        self,
        query: str,
        contexts,
        history: Optional[List[dict]] = None,
    ) -> str:
        prompt = build_prompt(query, contexts)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages)
