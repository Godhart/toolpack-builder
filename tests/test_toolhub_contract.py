import json
import pytest
from toolpack_builder.toolhub import pack, validate_pack_v1, ToolHubPackError


def test_toolhub_v1_pack_survives_json_roundtrip():
    payload = pack("demo", [{
        "name":"x","slug":"x","agentDescription":"x","code":"print(1)","packageJson":"",
        "inputSchema":{},"outputSchema":{},"examples":[],"timeoutMs":30000,
        "isMcpProxy":False,"mcpMethodName":None,"runnerType":"python_local","runnerName":"Python",
    }])
    restored = json.loads(json.dumps(payload))
    validate_pack_v1(restored)
    assert restored == payload


def test_toolhub_contract_rejects_wrong_version():
    payload = {"kind":"TOOLHUB_PACK","version":2,"category":{}}
    with pytest.raises(ToolHubPackError):
        validate_pack_v1(payload)
