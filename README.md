# DATABASE BACKUP/RESTORE COMMANDS

![Custom Badge](https://img.shields.io/badge/CRISP-26c70a)

### Dump Database
pg_dump -U postgres -F c -d crisp_database -h 127.0.0.1 -b -f path/to/backup.sql

Add the following Bash variable to get the time in the backup filename:
$(date -u +%Y.%m.%d.%H-%M)

### Restore Database
pg_restore -U postgres --clean -h 127.0.0.1 -d crisp_database path/to/backup.sql
