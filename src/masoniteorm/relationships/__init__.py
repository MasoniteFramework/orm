from .BelongsTo import BelongsTo as belongs_to
from .BelongsToMany import BelongsToMany
from .HasMany import HasMany as has_many
from .HasManyThrough import HasManyThrough as has_many_through
from .HasOne import HasOne as has_one
from .HasOneThrough import HasOneThrough as has_one_through
from .MorphMany import MorphMany as morph_many
from .MorphOne import MorphOne as morph_one
from .MorphTo import MorphTo as morph_to
from .MorphToMany import MorphToMany as morph_to_many

# Proper decorator for belongs_to_many

def belongs_to_many(local_key=None, foreign_key=None, local_owner_key=None, other_owner_key=None, table=None, with_timestamps=False, pivot_id="id", attribute="pivot", with_fields=None):
    def decorator(fn):
        def wrapper(self):
            return BelongsToMany(
                fn=fn,
                local_key=local_key,
                foreign_key=foreign_key,
                local_owner_key=local_owner_key,
                other_owner_key=other_owner_key,
                table=table,
                with_timestamps=with_timestamps,
                pivot_id=pivot_id,
                attribute=attribute,
                with_fields=with_fields or [],
            )
        return property(wrapper)
    return decorator
