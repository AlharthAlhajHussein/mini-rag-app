## Run Alembic Migrations

### Configration

```bash
cp alembic.ini.example alembic.ini
```

- Update the `alembic.ini` with your database credentials (`sqlalchemy.url`)

### Create new migration

```bash
alembic revision --autogenerate -m "Add ..."
```

### Upgreade the database
```bash
alembic upgrade head
```