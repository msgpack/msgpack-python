# Developer's note

### Build

```
$ make cython
```


### Test

MessagePack uses `pytest` for testing.
Run test with following command:

```
$ make test
```

### GitHub Actions dependencies

Workflow action versions are pinned in `.github/workflows/actions.lock`.
After changing a `uses:` reference or adding a workflow, regenerate and verify
the lockfile with the official GitHub CLI extension:

```
$ gh extension install github/gh-actions-lock
$ gh actions-lock --no-narrow
$ gh actions-lock --verify --no-narrow
```

Review and commit the workflow changes together with the generated lockfile.
Do not edit the lockfile by hand. Dependabot updates the corresponding lockfile
entries when it updates action versions in onboarded workflows.

Keep the PyPI publish action's SHA reference: it also uses the reference to
select its Docker image. `--no-narrow` preserves this reference.
