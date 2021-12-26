import pydoc


class Seeder:
    def __init__(self, dry=False, seed_path="databases/seeds"):
        self.ran_seeds = []
        self.dry = dry
        self.seed_path = seed_path
        self.seed_module = seed_path.replace("/", ".").replace("\\", ".")

    def call(self, *seeder_classes):
        for seeder_class in seeder_classes:
            self.ran_seeds.append(seeder_class)
            if not self.dry:
                seeder_class().run()

    def run_database_seed(self):
        database_seeder = pydoc.locate(
            f"{self.seed_module}.database_seeder.DatabaseSeeder"
        )

        self.ran_seeds.append(database_seeder)

        if not self.dry:
            database_seeder().run()

    def run_specific_seed(self, seed):
        file_name = f"{self.seed_module}.{seed}"
        database_seeder = pydoc.locate(file_name)

        if not database_seeder:
            raise ValueError(f"Could not find the {file_name} seeder file")

        self.ran_seeds.append(database_seeder)

        if not self.dry:
            database_seeder().run()
        else:
            print(f"Running {database_seeder}")
