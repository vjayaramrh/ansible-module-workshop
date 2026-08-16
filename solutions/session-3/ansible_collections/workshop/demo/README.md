# workshop.demo (reference solution)

Complete, passing solution for Session 3: `config_setting` with sanity, unit,
and integration tests.

Run from this directory:

```bash
ansible-test sanity --test validate-modules plugins/modules/config_setting.py
pytest tests/unit/plugins/modules/test_config_setting.py -v
ansible-test integration config_setting
```
