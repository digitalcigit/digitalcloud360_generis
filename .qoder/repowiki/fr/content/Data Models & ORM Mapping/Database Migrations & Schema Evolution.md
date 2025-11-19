# Database Migrations & Schema Evolution

<cite>
**Referenced Files in This Document**   
- [env.py](file://alembic/env.py)
- [2c43863b5e49_initial_migration.py](file://alembic/versions/2c43863b5e49_initial_migration.py)
- [d3ea4d165475_update_user_model_for_standalone_auth.py](file://alembic/versions/d3ea4d165475_update_user_model_for_standalone_auth.py)
- [f45c116fedf1_add_name_to_user_model.py](file://alembic/versions/f45c116fedf1_add_name_to_user_model.py)
- [user.py](file://app/models/user.py)
- [alembic.ini](file://alembic.ini)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Alembic Configuration and Environment Setup](#alembic-configuration-and-environment-setup)
3. [Migration File Structure and Revision Management](#migration-file-structure-and-revision-management)
4. [Schema Evolution: Initial Migration](#schema-evolution-initial-migration)
5. [Authentication Update Migration](#authentication-update-migration)
6. [User Model Enhancement Migration](#user-model-enhancement-migration)
7. [Model-Database Synchronization and Autogeneration](#model-database-synchronization-and-autogeneration)
8. [Best Practices for Migration Script Development](#best-practices-for-migration-script-development)
9. [Testing and Deployment Strategies](#testing-and-deployment-strategies)
10. [Conclusion](#conclusion)

## Introduction
This document provides comprehensive documentation for the Alembic migration system and schema evolution practices within the Genesis AI Service. It details the purpose, structure, and functionality of each migration script, explains the migration workflow, and outlines best practices for maintaining database schema integrity across development, testing, and production environments. The documentation covers the initial schema definition, authentication system updates, user model enhancements, and the process for generating new migrations through Alembic's autogenerate feature.

## Alembic Configuration and Environment Setup

The Alembic environment is configured through two primary files: `alembic.ini` and `env.py`. These files work together to establish the connection between the application's data models and the database, enabling schema migrations to be generated and applied systematically.

```mermaid
flowchart TD
A["alembic.ini"] --> B["Database URL Configuration"]
A --> C["Script Location"]
A --> D["Logging Configuration"]
E["env.py"] --> F["Async Database Connection"]
E --> G["Model Metadata Binding"]
E --> H["Online/Offline Mode"]
B --> E
C --> E
G --> E
F --> I["Migration Execution"]
H --> I
```

**Diagram sources**
- [env.py](file://alembic/env.py#L1-L87)
- [alembic.ini](file://alembic/alembic.ini#L1-L147)

**Section sources**
- [env.py](file://alembic/env.py#L1-L87)
- [alembic.ini](file://alembic/alembic.ini#L1-L147)

The `alembic.ini` file serves as the configuration entry point, specifying the script location, database URL, and logging parameters. The database URL is defined as `postgresql+asyncpg://genesis_user:${POSTGRES_PASSWORD}@postgres:5432/genesis_db`, which uses environment variable substitution for security. The `env.py` file contains the runtime logic for connecting to the database using SQLAlchemy's async engine and binding the application's model metadata (imported from `app.models.base`) to Alembic's migration context.

The configuration supports both online and offline migration modes. In online mode, an asynchronous connection is established using `create_async_engine`, and migrations are executed within a connection context. The `target_metadata = Base.metadata` line ensures that Alembic can compare the current state of the models with the database schema to detect changes during autogeneration.

## Migration File Structure and Revision Management

Alembic migration files follow a standardized structure that includes revision identifiers, dependency chains, and upgrade/downgrade operations. Each migration script is stored in the `alembic/versions/` directory with a filename format of `{revision_id}_{description}.py`.

```mermaid
classDiagram
class MigrationScript {
+str revision
+Union[str, Sequence[str], None] down_revision
+Union[str, Sequence[str], None] branch_labels
+Union[str, Sequence[str], None] depends_on
+upgrade() void
+downgrade() void
}
MigrationScript --> RevisionID : "has"
MigrationScript --> DependencyChain : "references"
MigrationScript --> UpgradeOperation : "contains"
MigrationScript --> DowngradeOperation : "contains"
class RevisionID {
+str revision
+str down_revision
}
class DependencyChain {
+list revision_chain
+validate_dependencies() bool
}
class UpgradeOperation {
+list operations
+execute_upgrade() void
}
class DowngradeOperation {
+list operations
+execute_downgrade() void
}
```

**Diagram sources**
- [2c43863b5e49_initial_migration.py](file://alembic/versions/2c43863b5e49_initial_migration.py#L1-L193)
- [d3ea4d165475_update_user_model_for_standalone_auth.py](file://alembic/versions/d3ea4d165475_update_user_model_for_standalone_auth.py#L1-L39)

**Section sources**
- [2c43863b5e49_initial_migration.py](file://alembic/versions/2c43863b5e49_initial_migration.py#L1-L193)
- [d3ea4d165475_update_user_model_for_standalone_auth.py](file://alembic/versions/d3ea4d165475_update_user_model_for_standalone_auth.py#L1-L39)

Each migration script contains several key components:
- **Revision ID**: A unique identifier for the migration (e.g., `2c43863b5e49`)
- **Down revision**: References the parent migration in the chain (None for initial migration)
- **Upgrade method**: Contains operations to apply the schema changes forward
- **Downgrade method**: Contains operations to revert the schema changes

The dependency chain is critical for maintaining the correct order of migrations. The `down_revision` field creates a linked list of migrations, ensuring they are applied in the proper sequence. For example, the `d3ea4d165475` migration has `down_revision = '2c43863b5e49'`, establishing it as a direct descendant of the initial migration.

## Schema Evolution: Initial Migration

The initial migration script (`2c43863b5e49_initial_migration.py`) establishes the foundational database schema with multiple interconnected tables that support the core functionality of the Genesis AI Service.

```mermaid
erDiagram
USERS {
integer id PK
string email UK
string name
string hashed_password
timestamp created_at
timestamp updated_at
}
USER_PROFILES {
integer id PK
integer user_id FK
string country
string city
string region
string preferred_language
string coaching_style
json cultural_context
json business_context
timestamp created_at
timestamp updated_at
}
BUSINESSES {
integer id PK
string business_name
string sector
integer user_id FK
text vision
text mission
text target_audience
text differentiation
text value_proposition
json location
json cultural_context
string status
timestamp created_at
timestamp updated_at
}
COACHING_SESSIONS {
integer id PK
integer user_id FK
string session_id UK
enum status
enum current_step
json step_completion
float coaching_confidence
integer retry_count
json cultural_context
json sector_context
json coaching_plan
json conversation_history
integer coaching_duration
timestamp created_at
timestamp updated_at
}
BUSINESS_BRIEFS {
integer id PK
integer coaching_session_id FK
string business_name
text vision
text mission
text target_audience
text differentiation
text value_proposition
string sector
json location
json market_research
json content_generation
json logo_creation
json seo_optimization
json template_selection
float overall_confidence
float brief_completeness
json is_ready_for_website
integer dc360_website_id
timestamp created_at
timestamp updated_at
}
BUSINESS_CONTEXTS {
integer id PK
integer business_id FK
json market_size
json competitors
json opportunities
json pricing_insights
json logo_assets
json color_palette
json brand_guidelines
json website_content
json seo_metadata
json marketing_content
string selected_template
json customizations
float market_confidence
float content_quality
float brand_consistency
string dc360_integration_status
integer dc360_website_id
timestamp created_at
timestamp updated_at
}
COACHING_STEPS {
integer id PK
integer session_id FK
enum step_name
integer step_order
text user_response
text coach_message
json examples_provided
json is_complete
float confidence_score
json validation_criteria
integer step_duration
timestamp created_at
timestamp updated_at
}
USERS ||--o{ USER_PROFILES : "1-to-1"
USERS ||--o{ BUSINESSES : "1-to-many"
USERS ||--o{ COACHING_SESSIONS : "1-to-many"
COACHING_SESSIONS ||--o{ COACHING_STEPS : "1-to-many"
COACHING_SESSIONS ||--o{ BUSINESS_BRIEFS : "1-to-1"
BUSINESSES ||--o{ BUSINESS_CONTEXTS : "1-to-1"
```

**Diagram sources**
- [2c43863b5e49_initial_migration.py](file://alembic/versions/2c43863b5e49_initial_migration.py#L1-L193)

**Section sources**
- [2c43863b5e49_initial_migration.py](file://alembic/versions/2c43863b5e49_initial_migration.py#L1-L193)

The initial schema includes six core tables:
- **users**: Stores user authentication information
- **user_profiles**: Extends user information with coaching preferences and context
- **businesses**: Represents business entities created by users
- **coaching_sessions**: Tracks AI coaching sessions for business development
- **business_briefs**: Stores the output of coaching sessions
- **business_contexts**: Maintains contextual data for business development
- **coaching_steps**: Records individual steps within coaching sessions

Each table inherits from a base model that includes `id`, `created_at`, and `updated_at` fields. The schema includes appropriate indexes for frequently queried fields such as email addresses, session IDs, and business names. Foreign key constraints ensure referential integrity between related entities.

## Authentication Update Migration

The `d3ea4d165475_update_user_model_for_standalone_auth.py` migration modifies the user model to support standalone authentication by adding password storage and removing legacy DigitalCloud360 integration fields.

```mermaid
flowchart TD
A["Initial User Schema"] --> B["Add hashed_password column"]
A --> C["Remove dc360_user_id column"]
A --> D["Remove name column"]
A --> E["Remove ix_users_dc360_user_id index"]
B --> F["Updated User Schema"]
C --> F
D --> F
E --> F
style A fill:#f9f,stroke:#333
style F fill:#bbf,stroke:#333
subgraph "Schema Changes"
B
C
D
E
end
```

**Diagram sources**
- [d3ea4d165475_update_user_model_for_standalone_auth.py](file://alembic/versions/d3ea4d165475_update_user_model_for_standalone_auth.py#L1-L39)

**Section sources**
- [d3ea4d165475_update_user_model_for_standalone_auth.py](file://alembic/versions/d3ea4d165475_update_user_model_for_standalone_auth.py#L1-L39)

This migration represents a significant architectural shift from relying on DigitalCloud360 for user authentication to implementing a standalone authentication system. The upgrade operations:
1. Add a `hashed_password` column to store bcrypt-hashed passwords
2. Remove the `dc360_user_id` column and its unique index, eliminating the dependency on external user IDs
3. Remove the `name` column (temporarily, as it will be re-added in a subsequent migration)

The downgrade operations reverse these changes, restoring the `dc360_user_id` and `name` columns and recreating the index. This bidirectional capability allows for safe rollback if issues arise after deployment. The migration maintains data integrity by using Alembic's schema modification operations that preserve existing user data while restructuring the table.

## User Model Enhancement Migration

The `f45c116fedf1_add_name_to_user_model.py` migration re-introduces the name field to the user model, completing the transition to a standalone authentication system with full user profile capabilities.

```mermaid
sequenceDiagram
participant Migration as Migration Script
participant Database as PostgreSQL
participant Model as User Model
Migration->>Database : ALTER TABLE users ADD COLUMN name
Database-->>Migration : Success
Migration->>Model : Update model definition
Model->>Application : Name field available
```

**Diagram sources**
- [f45c116fedf1_add_name_to_user_model.py](file://alembic/versions/f45c116fedf1_add_name_to_user_model.py#L1-L29)
- [user.py](file://app/models/user.py#L1-L42)

**Section sources**
- [f45c116fedf1_add_name_to_user_model.py](file://alembic/versions/f45c116fedf1_add_name_to_user_model.py#L1-L29)
- [user.py](file://app/models/user.py#L1-L42)

Interestingly, this migration script contains empty `upgrade()` and `downgrade()` methods, which suggests it may have been generated but not properly populated with the necessary operations. Based on the model definition in `app/models/user.py`, the intended upgrade operation should be:

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('name', sa.String(), nullable=False))
```

And the corresponding downgrade operation:

```python
def downgrade() -> None:
    op.drop_column('users', 'name')
```

The current implementation would not actually modify the schema, potentially causing a mismatch between the code model and database schema. This highlights the importance of reviewing autogenerate output before applying migrations. The User model in `app/models/user.py` confirms that the `name` field is required and should be present in the database schema.

## Model-Database Synchronization and Autogeneration

The Alembic system supports automatic migration generation by comparing the current state of SQLAlchemy models with the existing database schema. This process is configured through the `env.py` file, which imports the application's model metadata for comparison.

```mermaid
flowchart LR
A["SQLAlchemy Models"] --> C["Alembic Autogenerate"]
B["Database Schema"] --> C
C --> D["Migration Script"]
D --> E["Database"]
E --> |"Schema Reflection"| B
style C fill:#f96,stroke:#333
subgraph "Autogeneration Process"
A
B
C
D
end
```

**Diagram sources**
- [env.py](file://alembic/env.py#L1-L87)
- [user.py](file://app/models/user.py#L1-L42)

**Section sources**
- [env.py](file://alembic/env.py#L1-L87)
- [user.py](file://app/models/user.py#L1-L42)

The autogeneration process works as follows:
1. Alembic imports the `target_metadata` from the application's models (via `Base.metadata`)
2. It connects to the database and reflects the current schema
3. It compares the reflected schema with the model metadata to detect differences
4. It generates a new migration script with the necessary upgrade/downgrade operations

To generate a new migration, developers would typically run:
```bash
alembic revision --autogenerate -m "description of changes"
```

The `alembic.ini` configuration includes post-write hooks that could be used to automatically format or lint generated migration scripts, though these are currently commented out. The system is configured to use async database connections, which is essential for compatibility with the application's async architecture.

## Best Practices for Migration Script Development

Developing effective migration scripts requires adherence to several best practices to ensure data integrity, maintainability, and reliability across environments.

```mermaid
flowchart TD
A["Best Practices"] --> B["Test Migrations"]
A --> C["Review Autogenerated Code"]
A --> D["Preserve Data"]
A --> E["Idempotent Operations"]
A --> F["Document Changes"]
A --> G["Use Transactions"]
B --> H["Test in Staging"]
C --> I["Verify Operations"]
D --> J["Avoid DROP COLUMN"]
E --> K["Check Existence First"]
F --> L["Clear Upgrade/Downgrade Notes"]
G --> M["Wrap in Transaction"]
```

**Diagram sources**
- [2c43863b5e49_initial_migration.py](file://alembic/versions/2c43863b5e49_initial_migration.py#L1-L193)
- [d3ea4d165475_update_user_model_for_standalone_auth.py](file://alembic/versions/d3ea4d165475_update_user_model_for_standalone_auth.py#L1-L39)

**Section sources**
- [2c43863b5e49_initial_migration.py](file://alembic/versions/2c43863b5e49_initial_migration.py#L1-L193)
- [d3ea4d165475_update_user_model_for_standalone_auth.py](file://alembic/versions/d3ea4d165475_update_user_model_for_standalone_auth.py#L1-L39)

Key best practices include:
- **Always test migrations**: Run migrations on a copy of production data before deployment
- **Review autogenerated scripts**: The `f45c116fedf1` migration demonstrates how autogenerated scripts may require manual correction
- **Preserve data**: Use `op.alter_column()` with `existing_type` when changing column types to avoid data loss
- **Write reversible migrations**: Ensure downgrade operations can safely revert changes
- **Use transactions**: Alembic automatically wraps migrations in transactions, but complex operations should be carefully designed
- **Add descriptive revision messages**: The revision ID should be accompanied by a clear description of changes
- **Handle dependencies explicitly**: When migrations depend on external systems, document these requirements

For data migrations (moving or transforming existing data), separate scripts should be created that operate on the data rather than the schema. These should be tested extensively to ensure data consistency.

## Testing and Deployment Strategies

Effective testing and deployment strategies are essential for reliable database schema evolution across different environments.

```mermaid
sequenceDiagram
participant Dev as Developer
participant CI as CI/CD Pipeline
participant Test as Test Environment
participant Prod as Production
Dev->>Dev : Create migration
Dev->>Dev : Test locally
Dev->>CI : Commit to repository
CI->>Test : Apply migration
Test->>Test : Run integration tests
Test-->>CI : Test results
CI->>Prod : Deploy if tests pass
Prod->>Prod : Apply migration
Prod->>Prod : Verify application
```

**Diagram sources**
- [test_db_connection.py](file://scripts/test_db_connection.py#L1-L26)
- [setup_dev_environment.py](file://scripts/setup_dev_environment.py#L1-L268)

**Section sources**
- [test_db_connection.py](file://scripts/test_db_connection.py#L1-L26)
- [setup_dev_environment.py](file://scripts/setup_dev_environment.py#L1-L268)

The project includes several tools to support testing and deployment:
- `test_db_connection.py`: Validates database connectivity, which is essential before applying migrations
- `setup_dev_environment.py`: Automates environment setup, ensuring consistency across developer machines

Recommended deployment strategies include:
1. **Staged rollout**: Apply migrations to development, then staging, then production
2. **Backup before migration**: Always backup the database before applying schema changes
3. **Monitor after deployment**: Verify application functionality and database performance post-migration
4. **Rollback plan**: Have a tested downgrade path available in case of issues

For zero-downtime deployments, migrations should be designed in two phases:
- Phase 1: Apply non-breaking changes (adding columns, creating indexes)
- Phase 2: Deploy application code that uses the new schema
- Phase 3: Remove deprecated fields (if necessary)

This approach ensures that the application remains functional throughout the deployment process.

## Conclusion
The Alembic migration system in the Genesis AI Service provides a robust framework for managing database schema evolution. Through a combination of automated detection and manual refinement, the system enables safe and reliable schema changes across development, testing, and production environments. The migration history demonstrates a clear progression from an initial schema to a more sophisticated standalone authentication system. Key strengths include proper dependency management, comprehensive schema definition, and integration with the application's async architecture. However, the empty migration script `f45c116fedf1_add_name_to_user_model.py` highlights the importance of reviewing autogenerated migrations before deployment. By following best practices for testing, documentation, and deployment, the team can continue to evolve the database schema while maintaining data integrity and application reliability.