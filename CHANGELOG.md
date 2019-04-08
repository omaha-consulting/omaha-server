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
