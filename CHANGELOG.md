# Change Log
 
## [3.0.0] - 2025-03-30
   
### Changed

- Model `create` now always checks for cast values 
- `pendulum` version upgrade

#### Breaking Changes

- Changed raw expressions placeholder from requiringing explicit quoring per grammar (like this '?') to automaic (like this ?)
- Changed `update` and `delete` methods to return the affected rows instead of the model
- Seeding depencies are now in a separate`[seeder]` extension
- `Factory` class must now be imported from the sub-package `masoniteorm.factories`
  
### Fixed

 - Model `update` and `delete` not casting passed values


## [2.24.0] - 2025-01-23
 
### Added
   
- allow override of model default selects

## [2.23.2] - 2024-11-29

## Added

- Ability so specify default select criteria for Models
- Add connection pooling to MySQL and Postgres
- PostgresConnection supports SSL and TLS options

## Fixed

- `.on_null` and `.on_not_null` had to be last criteria
- Find cannot use scopes
- Fix `has_one_through` relationship not working
- Tests parameter `query=True` should return query builder
- Fix `has_many_through` relationship not working
- Fixed nested relations

## [2.23.1] - 2024-10-22

Maintenance release 

## [2.23.0] - 2024-10-19

## Added

- Updated tests
