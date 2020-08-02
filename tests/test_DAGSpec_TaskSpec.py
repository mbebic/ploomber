import os
from pathlib import Path
import pytest
from ploomber.spec.TaskSpec import TaskSpec
from ploomber.spec.DAGSpec import DAGSpec, Meta
from ploomber.tasks import NotebookRunner, SQLScript, SQLDump
from ploomber import DAG


@pytest.mark.parametrize('spec, expected', [
    [{
        'source': 'sample.py',
        'product': 'out.ipynb'
    }, NotebookRunner],
    [{
        'source': 'sample.sql',
        'product': ['schema', 'table'],
        'client': 'db.get_client'
    }, SQLScript],
    [{
        'source': 'sample-select.sql',
        'product': 'file.csv',
        'class': 'SQLDump',
        'client': 'db.get_client'
    }, SQLDump],
])
def test_initialization(spec, expected, tmp_sample_tasks,
                        add_current_to_sys_path):
    meta = Meta.default_meta({
        'extract_product': False,
        'extract_upstream': True
    })

    spec = TaskSpec(spec, meta=meta)
    assert spec['class'] == expected
    # from IPython import embed
    # embed()

    spec.to_task(dag=DAG(), root_path='.')


@pytest.mark.parametrize('key', ['source', 'product'])
def test_validate_missing_source(key):
    with pytest.raises(KeyError):
        TaskSpec({key: None}, {
            'extract_product': False,
            'extract_upstream': False
        })


@pytest.mark.parametrize('task, meta', [
    ({
        'upstream': 'some_task',
        'product': None,
        'source': None
    }, {
        'extract_upstream': True,
        'extract_product': False
    }),
    ({
        'product': 'report.ipynb',
        'source': None
    }, {
        'extract_product': True,
        'extract_upstream': False
    }),
])
def test_error_if_extract_but_keys_declared(task, meta):
    with pytest.raises(ValueError):
        TaskSpec(task, meta)


def test_add_hook(tmp_directory, add_current_to_sys_path):
    task = {
        'product': 'notebook.ipynb',
        'source': 'source.py',
        'on_finish': 'hooks.some_hook',
        'on_render': 'hooks.some_hook',
        'on_failure': 'hooks.some_hook'
    }
    meta = Meta.default_meta()
    meta['extract_product'] = False

    Path('source.py').write_text("""
# + tags=["parameters"]
# some code
    """)

    Path('hooks.py').write_text("""

def some_hook():
    pass
    """)

    dag = DAG()
    t, _ = TaskSpec(task, meta).to_task(dag, root_path=os.getcwd())
    assert t.on_finish
    assert t.on_render
    assert t.on_failure
