import sys
import os
from types import SimpleNamespace


import importlib


def _install_fake_openai(content: str):
    # Create a minimal fake 'openai' module with the expected interface
    class _Completions:
        def __init__(self, content: str):
            self._content = content

        def create(self, **kwargs):
            class _Choice:
                def __init__(self, content):
                    self.message = SimpleNamespace(content=content)

            class _Resp:
                def __init__(self, content):
                    self.choices = [_Choice(content)]
            return _Resp(self._content)

    class _OpenAI:
        def __init__(self, base_url=None, api_key=None):
            self.base_url = base_url
            self.api_key = api_key
            self.chat = SimpleNamespace(completions=_Completions(content))

    mod = SimpleNamespace(OpenAI=_OpenAI)
    sys.modules['openai'] = mod
    return mod


def _load_target_module():
    # Import the dynamic tool agent module by adjusting PYTHONPATH so the
    # relative path ../../DynamicToolAgent is importable.
    here = os.path.dirname(__file__)
    target_dir = os.path.abspath(os.path.join(here, '..', '..', 'DynamicToolAgent'))
    if target_dir not in sys.path:
        sys.path.insert(0, target_dir)
    # Import the module under its file name (not a package).
    import dynamic_tool_agent_persisted as mod
    importlib.reload(mod)
    return mod


def test_call_llm_openai_backend(monkeypatch):
    # Prepare fake OpenAI module returning a deterministic value
    _install_fake_openai(content="OPENAI_OK")

    mod = _load_target_module()
    os.environ['AGENT_LLM_BACKEND'] = 'openai'
    os.environ['AGENT_MODEL'] = 'gpt-4.1-mini'
    # Should not crash and return the fake content
    result = mod.call_llm([{"role": "user", "content": "test"}], system="sys")
    assert result == "OPENAI_OK"


def test_call_llm_local_backend(monkeypatch):
    # Prepare fake OpenAI module returning a deterministic value for local backend
    _install_fake_openai(content="LOCAL_OK")

    mod = _load_target_module()
    os.environ['AGENT_LLM_BACKEND'] = 'local'
    os.environ['AGENT_BASE_URL'] = 'http://localhost:8080/v1'
    os.environ['AGENT_MODEL'] = 'local-model'
    result = mod.call_llm([{"role": "user", "content": "test"}], system="sys")
    assert result == "LOCAL_OK"


def test_call_llm_unsupported_backend_raises():
    mod = _load_target_module()
    os.environ['AGENT_LLM_BACKEND'] = 'unknown_backend'
    try:
        mod.call_llm([{"role": "user", "content": "test"}], system="sys")
    except ValueError as e:
        assert "Unsupported LLM_BACKEND" in str(e)
    else:
        raise AssertionError("Expected ValueError for unsupported backend")
