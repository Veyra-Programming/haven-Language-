"""
Custom language pipeline adapters and pipe operator interoperability.
Supports Haven's native `|>` and `into` operators, as well as Python `|` bitwise-or piping.
"""

from typing import Any, Callable, Dict, Optional, Union, List


class Pipeable:
    """
    Wrapper enabling functional pipelining:
      input_val |> pipeable
      input_val | pipeable
      pipeable(input_val)
    """
    def __init__(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self.func: Callable[..., Any] = func
        self.args: tuple[Any, ...] = args
        self.kwargs: Dict[str, Any] = kwargs

    def __call__(self, *call_args: Any, **call_kwargs: Any) -> Any:
        # Merge keyword arguments
        merged_kwargs = {**self.kwargs, **call_kwargs}
        if self.args:
            return self.func(*(self.args + call_args), **merged_kwargs)
        return self.func(*call_args, **merged_kwargs)

    def __ror__(self, other: Any) -> Any:
        """Enables Python standard pipe: data | pipeable"""
        return self(other)

    def __repr__(self) -> str:
        fn_name = getattr(self.func, "__name__", str(self.func))
        return f"Pipeable({fn_name})"


def pipe_fn(
    client_or_method: Any,
    model: str = "meta-llama/Llama-3.3-70B-Instruct",
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    **extra_kwargs: Any
) -> Pipeable:
    """
    Generate a functional pipeline transformer suitable for:
      "Explain Haven" |> pipe_fn(client) |> print
      "Summarize" into pipe_fn(client) into print
    """
    def _transform(user_input: Union[str, List[Dict[str, str]], Any]) -> str:
        if isinstance(user_input, str):
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_input})
        elif isinstance(user_input, list):
            messages = user_input
        else:
            messages = [{"role": "user", "content": str(user_input)}]

        # Determine target chat callable
        chat_callable = getattr(client_or_method, "chat", client_or_method)
        response = chat_callable(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **extra_kwargs
        )

        if hasattr(response, "content"):
            return response.content
        return str(response)

    return Pipeable(_transform)
