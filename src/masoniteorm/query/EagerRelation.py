class EagerRelations:
    def __init__(self, relation=None):
        self.eagers = []
        self.nested_eagers = {}
        self.callback_eagers = {}
        self.is_nested = False
        self.relation = relation

    def register(self, *relations, callback=None):
        for relation in relations:
            if isinstance(relation, str):
                if "." in relation:
                    self.is_nested = True
                    parts = relation.split(".")
                    current = self.nested_eagers
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            if part not in current:
                                current[part] = []
                        else:
                            if part not in current:
                                current[part] = {}
                            current = current[part]
                else:
                    self.eagers.append(relation)
            elif isinstance(relation, (tuple, list)):
                for eagers in relations:
                    for eager in eagers:
                        self.register(eager)
            elif isinstance(relation, dict):
                self.callback_eagers.update(relation)

        return self

    def get_eagers(self):
        eagers = []
        if self.eagers:
            eagers.append(self.eagers)

        if self.nested_eagers:
            eagers.append(self.nested_eagers)

        if self.callback_eagers:
            eagers.append(self.callback_eagers)

        return eagers
