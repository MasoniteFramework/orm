class EagerRelations:
    def __init__(self, relation=None):
        self.eagers = []
        self.nested_eagers = {}
        self.is_nested = False
        self.relation = relation

    def register(self, *relations):
        for relation in relations:
            if isinstance(relation, str) and "." not in relation:
                self.eagers += [relation]
            elif isinstance(relation, str) and "." in relation:
                self.is_nested = True
                relation_key = relation.split(".")[0]
                if relation_key not in self.nested_eagers:
                    self.nested_eagers = {relation_key: relation.split(".")[1:]}
                else:
                    self.nested_eagers[relation_key] += relation.split(".")[1:]
            elif isinstance(relation, (tuple, list)):
                for eagers in relations:
                    for eager in eagers:
                        self.register(eager)

        return self

    def get_eagers(self):
        eagers = []
        if self.eagers:
            eagers.append(self.eagers)

        if self.nested_eagers:
            eagers.append(self.nested_eagers)

        return eagers
