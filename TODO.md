- [x] fix scopes - need to find a new way to perform scopes

- [x] scopes need to be set on the model and then passed off to the query builder

- [x] global scopes
    - on select need to call a scope
    - on delete need to call a scope
    - need to be able to remove global scopes
    - need to be able to able to call something like with_trashed()
        - this needs to remove global scopes only from the soft deletes class 