from langchain_components.runtime.context import RuntimeContext


class RuntimeLifecycle:
    def before_plan(self, context: RuntimeContext):
        ...

    def after_plan(self, context: RuntimeContext):
        ...

    def before_execution(self, context: RuntimeContext):
        ...

    def after_execution(self, context: RuntimeContext):
        ...

    def before_finish(self, context: RuntimeContext):
        ...

    def after_finish(self, context: RuntimeContext):
        ...