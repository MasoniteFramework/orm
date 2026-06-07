import warnings

warnings.warn(
    "The 'masonite-orm' package is unmaintained and will receive no further "
    "updates. Masonite ORM continues as 'masonite-framework-orm' "
    "(https://github.com/masonitedev/orm) — imports are unchanged. "
    "Documentation: https://docs.masonite.dev",
    FutureWarning,
    stacklevel=2,
)

from .models import Model
