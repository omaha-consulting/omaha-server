## [0.7.2] - 2019-05-07
Update Python version to 3.7

#### Updated dependencies
- django-debug-panel: `0.8.2` -> `latest`
- xmlunittest: `0.3.2` -> `latest`
- django: `1.11.0` -> `1.11.17`
- django-absolute: `0.3` -> `latest`
- django-redis: `4.4.3` -> `latest`
- django-cacheops: `2.4.3` -> `latest`
- django-ace: `1.0.2` -> `latest`
- django-select2: `latest` -> `6.3.1`
- celery: `3.1.23` -> `4.3.0`
- redis: `2.10.6` -> `latest`
- raven: `5.17.0` -> `latest`
- protobuf-to-dict -> protobuf3-to-dict

## [0.7.2] - 2019-03-12
Changed base image from Ubuntu:14.04 to Alpine:3.9 version. Update Django library from 1.9.6 to 1.11.0 version.

#### Fixed Django's deprecated issues
- Removed import `TEMPLATE_CONTEXT_PROCESSORS`.
- Replaced `notmigrations` to `None` in `MIGRATION_MODULES`.
- Redefined `add_arguments` instead use `BaseCommand.option_list`.
- Replaced `get_field_by_name` to `get_field`.
- Fixed issue with non-relational fields for nested relations(`select_related`).

#### Updated dependencies
- djangorestframework: `3.3.3` -> `3.4.0`
- django-filter: `0.13.0` -> `1.0.2`
- django-nose: `1.4.3` -> `1.4.5`
- django-bootstrap3: `7.0.1` -> `latest`
- django-select2: `5.8.4` -> `latest`
- nose: `1.3.7` -> `latest`
- markdown: `2.6.6` -> `2.6.11`
- protobuf: `3.3.0` -> `latest`
