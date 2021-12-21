class CanOverrideOptionsDefault:
    """Command mixin to allow to override optional argument default values when instantiating the
    command.

    Example: SomeCommand(app, option1="other/default").
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.overriden_default = kwargs
        for name, value in self.overriden_default.items():
            option = self.config.options.get(name)
            if option:
                option.set_default(value)
