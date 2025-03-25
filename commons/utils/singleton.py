class Singleton:
    _init = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Singleton, cls).__new__(cls)

        return cls.instance

    @classmethod
    def is_init(cls):
        return cls._init

    @classmethod
    def set_init(cls):
        cls._init = True
