# workshop.web (reference solution)

Complete capstone: `webhook_resource` manages a named resource on a REST API,
idempotently, with check mode and a mocked unit test.

```bash
# unit tests (no network)
pytest tests/unit/plugins/modules/test_webhook_resource.py -v

# build + install + run against the mock API (see exercises/session-4/mock_api.py)
export ANSIBLE_COLLECTIONS_PATH=/tmp/ws-collections
ansible-galaxy collection build --force
ansible-galaxy collection install workshop-web-1.0.0.tar.gz -p /tmp/ws-collections --force
```

Verified end to end: `state=present` reports `changed`, a second `present` is a
no-op, and `state=absent` reports `changed`.
