# API REST con pipeline CI/CD

API de usuarios con 6 endpoints, pruebas (cobertura mínima 70 %), imagen Docker y despliegue automático a una EC2 con GitHub Actions.

Esta carpeta es la raíz del repositorio de GitHub. El workflow solo se ejecuta si `.github/workflows/main.yml` queda en la raíz del repo.

## Endpoints

| Método | Ruta | Qué hace |
| --- | --- | --- |
| GET | `/api/health` | Estado de la API y el mensaje de la demo |
| GET | `/api/users` | Lista los usuarios |
| POST | `/api/users` | Crea un usuario (`name`, `email`) |
| GET | `/api/users/<id>` | Devuelve un usuario |
| PUT | `/api/users/<id>` | Reemplaza `name` y `email` |
| DELETE | `/api/users/<id>` | Elimina un usuario |

Ejemplo:

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Ana\",\"email\":\"ana@example.com\"}"
```

## Correr en local

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
$env:DB_PATH = "data/users.db"
flask --app wsgi run --port 8000
```

`pytest` muestra la tabla de cobertura y falla si baja de 70 %.

## Docker en local

```powershell
docker build -t rest-api-cicd .
docker run --rm -p 8000:80 rest-api-cicd
```

En la EC2 el mismo contenedor se publica en el puerto 80.

## Secrets de GitHub

No van en el código. En el repositorio: Settings, Secrets and variables, Actions.

| Secret | Valor |
| --- | --- |
| `DOCKERHUB_USERNAME` | Usuario de Docker Hub |
| `DOCKERHUB_TOKEN` | Personal Access Token de Docker Hub (permiso de escritura) |
| `EC2_HOST` | IP pública o DNS de la instancia |
| `EC2_USER` | Usuario SSH. En Amazon Linux es `ec2-user` |
| `EC2_SSH_KEY` | Contenido completo del archivo `.pem` |

## EC2 (una vez)

1. Instancia Amazon Linux 2023 (el enunciado también acepta Ubuntu; los comandos de este repo son para Amazon Linux).
2. Security Group: puerto 22 (SSH) y puerto 80 (HTTP).
3. Entrar por SSH y ejecutar los comandos de `scripts/bootstrap-ec2.sh`.
4. Cerrar la sesión y volver a entrar, para que el usuario quede en el grupo `docker`.
5. Guardar los secrets y hacer push a `main`.

El workflow, en cada push a `main`:

1. Corre las pruebas y escribe la cobertura en el log.
2. Entra a Docker Hub con el PAT.
3. Construye la imagen y la publica con los tags `latest` y el hash del commit (`github.sha`).
4. Por SSH descarga esa imagen, detiene el contenedor anterior y levanta el nuevo en el puerto 80.

Un pull request a `main` solo corre las pruebas. No publica ni despliega.

## Demo en vivo

Edita el mensaje en `app/settings.py`, haz commit y push a `main`. Cuando el workflow termine:

```bash
curl http://<IP_EC2>/api/health
```

La respuesta debe traer el mensaje nuevo.
