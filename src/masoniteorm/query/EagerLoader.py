from typing import Any, Dict, List, Optional, Union, Callable, TYPE_CHECKING
from ..collection import Collection
from ..exceptions import ModelNotFound

if TYPE_CHECKING:
    from ..models.Model import Model

class EagerLoadRelation:
    """Represents a single eager load relation with its nested relations."""
    
    def __init__(self, name: str, nested: Optional[Dict[str, Any]] = None):
        self.name = name
        self.nested = nested or {}
        
    def __str__(self) -> str:
        return self.name
        
    def __repr__(self) -> str:
        return f"EagerLoadRelation(name='{self.name}', nested={self.nested})"

class EagerLoader:
    """Handles eager loading of relationships in a clean and efficient way."""
    
    def __init__(self, model: 'Model'):
        self.model = model
        self.relations: List[EagerLoadRelation] = []
        self.callback_relations: Dict[str, Callable] = {}
        
    def register(self, *relations: Union[str, Dict[str, Any], List[str]]) -> 'EagerLoader':
        """Register relationships to be eager loaded.
        
        Args:
            *relations: Variable length list of relationships to eager load.
                       Can be strings, dictionaries, or lists.
                       
        Returns:
            self
        """
        print(f"[EagerLoader] Registering relations: {relations}")
        for relation in relations:
            if isinstance(relation, str):
                if "." in relation:
                    # Handle nested relationships like "posts.comments"
                    parts = relation.split(".")
                    nested = {}
                    current = nested
                    
                    # Build the nested structure
                    for i, part in enumerate(parts):
                        if i == 0:
                            # Root relation
                            current[part] = {}
                            current = current[part]
                        elif i == len(parts) - 1:
                            # Last part
                            current[part] = {}
                        else:
                            # Middle parts
                            current[part] = {}
                            current = current[part]
                            
                    # Add the root relation with the full nested structure
                    self.relations.append(EagerLoadRelation(parts[0], nested[parts[0]]))
                    print(f"[EagerLoader] Nested structure: {nested}")
                else:
                    # Handle simple relationships
                    self.relations.append(EagerLoadRelation(relation))
            elif isinstance(relation, (list, tuple)):
                # Handle lists of relationships
                for r in relation:
                    self.register(r)
            elif isinstance(relation, dict):
                # Handle callback relationships and nested dictionaries
                for name, value in relation.items():
                    if isinstance(value, dict):
                        # This is a nested relationship
                        self.relations.append(EagerLoadRelation(name, value))
                    else:
                        # This is a callback relationship
                        self.callback_relations[name] = value
                        self.relations.append(EagerLoadRelation(name))
        
        print(f"[EagerLoader] Registered relations: {self.relations}")
        return self
        
    def _register_nested(self, relation: str) -> None:
        """Register a nested relationship.
        
        Args:
            relation: The nested relationship string (e.g. "posts.comments")
        """
        print(f"[EagerLoader] Registering nested relation: {relation}")
        parts = relation.split(".")
        
        # Build the nested structure
        nested = {}
        current = nested
        
        # Build the structure from top to bottom
        for i, part in enumerate(parts):
            if i == 0:
                # Root relation
                current[part] = {}
                current = current[part]
            elif i == len(parts) - 1:
                # Last part
                current[part] = {}
            else:
                # Middle parts
                current[part] = {}
                current = current[part]
                
        # Add the root relation with the full nested structure
        self.relations.append(EagerLoadRelation(parts[0], nested[parts[0]]))
        print(f"[EagerLoader] Nested structure: {nested}")
                
    def load(self, models: Union['Model', Collection]) -> Union['Model', Collection]:
        """Load all registered relationships for the given models.
        
        Args:
            models: A single model or collection of models to load relationships for
            
        Returns:
            The models with their relationships loaded
        """
        if not models:
            return models
            
        # Convert single model to collection for consistent handling
        if not isinstance(models, Collection):
            models = Collection([models])
            
        print(f"[EagerLoader] Loading relations for model: {self.model.__class__.__name__}")
        # Load all relations
        for relation in self.relations:
            try:
                print(f"[EagerLoader] Loading relation: {relation.name}")
                # Get the relationship definition from the model class
                related = getattr(self.model.__class__, relation.name)
                
                if relation.name in self.callback_relations and callable(self.callback_relations[relation.name]):
                    # Handle callback relationships
                    callback = self.callback_relations[relation.name]
                    base_query = related.get_related(models, models)
                    related_models = callback(base_query)
                else:
                    # Handle regular relationships
                    related_models = related.get_related(models, models)
                
                print(f"[EagerLoader] Got related models for {relation.name}: {related_models}")
                
                # Register the relationship
                self._register_relationship(models, relation.name, related_models)
                
                # Load nested relations if any
                if relation.nested:
                    print(f"[EagerLoader] Loading nested relations for {relation.name}: {relation.nested}")
                    # Create a new loader for the nested level
                    if isinstance(related_models, Collection) and related_models:
                        nested_model = related_models[0]
                    else:
                        nested_model = related_models
                        
                    if nested_model:
                        nested_loader = EagerLoader(nested_model)
                        
                        # Register the nested relations
                        for nested_relation_name, nested_nested in relation.nested.items():
                            if isinstance(nested_nested, dict):
                                nested_loader.register({nested_relation_name: nested_nested})
                            else:
                                nested_loader.register(nested_relation_name)
                                
                        # Load the nested relations
                        nested_loader.load(related_models)
                    
            except AttributeError as e:
                print(f"[EagerLoader] Error loading relation {relation.name}: {str(e)}")
                raise ModelNotFound(f"Relationship '{relation.name}' not found on model {self.model.__class__.__name__}")
            
        return models.first() if len(models) == 1 else models
        
    def _load_nested_relations(self, models: Collection, relations: Dict[str, Any]) -> None:
        """Load nested relationships recursively.
        
        Args:
            models: Collection of models to load relationships for
            relations: Dictionary of nested relationships to load
        """
        if not models:
            return
            
        print(f"[EagerLoader] Loading nested relations: {relations}")
        for relation_name, nested in relations.items():
            all_related = []
            
            # Get all related models for this relation
            for model in models:
                try:
                    print(f"[EagerLoader] Getting related models for {relation_name} on model {model.__class__.__name__}")
                    related_relationship = getattr(model.__class__, relation_name)
                    related_models = related_relationship.get_related(None, model)
                    
                    print(f"[EagerLoader] Got related models: {related_models}")
                    
                    # Register the relationship on the parent model
                    model.add_relation({relation_name: related_models})
                    
                    # Collect all related models for the next level of nesting
                    if isinstance(related_models, Collection):
                        all_related.extend(list(related_models))
                    elif related_models:
                        all_related.append(related_models)
                except AttributeError as e:
                    print(f"[EagerLoader] Error getting related models for {relation_name}: {str(e)}")
                    continue
                    
            # If we have related models and nested relations to load
            if all_related and nested:
                print(f"[EagerLoader] Creating nested loader for {len(all_related)} models")
                # Create a new loader for the nested level
                nested_loader = EagerLoader(all_related[0].__class__)
                
                # Register the nested relations
                if isinstance(nested, dict):
                    for nested_relation_name, nested_nested in nested.items():
                        if nested_nested:
                            nested_loader.register({nested_relation_name: nested_nested})
                        else:
                            nested_loader.register(nested_relation_name)
                else:
                    nested_loader.register(nested)
                    
                # Load the nested relations
                nested_loader.load(Collection(all_related))
        
    def _register_relationship(self, models: Collection, relation_name: str, related_models: Collection) -> None:
        """Register a relationship on the models.
        
        Args:
            models: The models to register the relationship on
            relation_name: The name of the relationship
            related_models: The related models to register
        """
        print(f"[EagerLoader] Registering relationship {relation_name} with {len(related_models)} related models")
        
        # Get the relationship definition
        relationship = getattr(self.model.__class__, relation_name)
        
        # Register the relationship on each model
        for model in models:
            # Use the relationship's register_related method
            relationship.register_related(relation_name, model, related_models)
            
        return models 