from pathlib import Path
from toolpack_builder.builder import BuildConfig
from toolpack_builder.events import BuildEvent
from toolpack_builder.project import ProjectConfig
from toolpack_builder.toolhub import pack_from_paths, validate_pack_v1

def test_fingerprint_changes_with_config(tmp_path):
 a=BuildConfig(tmp_path, category_name='A'); b=BuildConfig(tmp_path, category_name='B'); assert a.fingerprint()!=b.fingerprint()

def test_project_roundtrip(tmp_path):
 p=tmp_path/'p.json'; x=ProjectConfig(source='/x',excludes=['**/x/**'],category_mode='directories'); x.save(p); assert ProjectConfig.load(p)==x

def test_directory_categories(tmp_path):
 root=tmp_path; path=root/'network'/'dns'/'resolve.py'; path.parent.mkdir(parents=True); path.touch()
 tool={'name':'resolve','slug':'resolve','agentDescription':'x','code':'x','packageJson':'x','inputSchema':{},'outputSchema':{},'examples':[],'timeoutMs':1,'isMcpProxy':False,'mcpMethodName':None,'runnerType':'python_local','runnerName':'Python'}
 payload=pack_from_paths('Root',[(path,tool)],root); validate_pack_v1(payload)
 c=payload['category']['children'][0]; assert c['name']=='network'; assert c['children'][0]['name']=='dns'; assert c['children'][0]['tools'][0]['name']=='resolve'

def test_event_model():
 e=BuildEvent('probe_started',1,3,Path('a.py')); assert e.total==3
