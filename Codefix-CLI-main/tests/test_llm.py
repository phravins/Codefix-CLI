import pytest
import asyncio
from unittest.mock import patch, MagicMock
from codefixcli.debugger.llm import ask_ollama, ask_ollama_async, build_prompt

def test_build_prompt():
    code = "def foo(): pass"
    prompt = build_prompt(code, {}, {})
    assert "def foo(): pass" in prompt

@patch("codefixcli.debugger.llm._get_session")
def test_ask_ollama_success(mock_get_session):
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "def fixed(): pass"}
    mock_response.raise_for_status.return_value = None
    mock_session.post.return_value = mock_response
    mock_get_session.return_value = mock_session

    res = ask_ollama("test prompt")
    assert res == "def fixed(): pass"
    mock_session.post.assert_called_once()

@patch("codefixcli.debugger.llm._get_session")
def test_ask_ollama_async_success(mock_get_session):
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "def fixed(): pass"}
    mock_response.raise_for_status.return_value = None
    mock_session.post.return_value = mock_response
    mock_get_session.return_value = mock_session

    res = asyncio.run(ask_ollama_async("test prompt"))
    assert res == "def fixed(): pass"
    mock_session.post.assert_called_once()
