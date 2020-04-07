class TimeStamps:
    def boot_timestamps():
        return {
            "update": TimeStamps.set_timestamp,
            "insert": TimeStamps.set_timestamp_create,
        }

    def set_timestamp(owner_cls, query):
        owner_cls.updated_at = "now"

    def set_timestamp_create(owner_cls, query):
        owner_cls.builder.create({"updated_at": "now", "created_at": "now"})
