"""
Workflow package.

Workflow modules are imported explicitly by the workflow registry.
Keeping package initialization lightweight prevents unrelated workflow
dependencies from being loaded when importing a single workflow.
"""