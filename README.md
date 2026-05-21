# encuestas-railway

App de encuestas con Flask y MySQL, lista para desplegar en Railway.

## Requisitos

- Python 3.11
- MySQL (o servicio MySQL en Railway)
- Railway CLI / Railway Dashboard

## Archivos importantes

- `Dockerfile` — define la imagen Docker para Railway
- `railway.json` — configuración de build/deploy
- `config.py` — carga `MYSQL_URL` / `DATABASE_URL` y transforma la URL para SQLAlchemy
- `mysql_schema.sql` — esquema MySQL para crear la base de datos y tablas
- `.env.example` — variables de entorno de ejemplo

## Deployment en Railway

1. Agrega un proyecto nuevo en Railway.
2. Selecciona `Deploy from GitHub` o sube tu repositorio.
3. En `Settings > Environment`, agrega estas variables:
   - `SECRET_KEY` con una cadena larga y secreta.
   - `MYSQL_URL` con la URL que Railway provee para el servicio MySQL.

Railway crea `MYSQL_URL` con el formato:

```
mysql://usuario:password@host:puerto/base_de_datos
```

`config.py` convierte automáticamente esa URL para SQLAlchemy.

4. Si usas Docker, Railway usará `Dockerfile` automáticamente.
5. Asegúrate de que el servicio MySQL esté activo y enlazado al proyecto.

## Uso local

1. Copia `.env.example` a `.env`.
2. Ajusta `SECRET_KEY` y `MYSQL_URL` a tus credenciales locales.
3. Crea la base de datos en MySQL con `mysql_schema.sql`:

```bash
mysql -u root -p < mysql_schema.sql
```

4. Ejecuta la app:

```bash
python run.py
```

## Notas

- `run.py` ahora usa `PORT` si está definido, para compatibilidad con Railway.
- `dockerignore` ya excluye `.env`, `__pycache__` y archivos de entorno.
