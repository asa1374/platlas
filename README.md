# platlas

Platform + Atlas. 플랫폼 지도를 그려주는 서비스.

## Backend 개발 환경

`/backend` 디렉터리에는 FastAPI 기반 API 서버와 Alembic 마이그레이션이 포함되어 있습니다.

### 로컬 실행

```bash
cp backend/.env.example backend/.env
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend/app
```

### 데이터베이스 마이그레이션

```bash
cd backend
alembic upgrade head
```

### Docker Compose

PostgreSQL, Redis, FastAPI 컨테이너를 한 번에 구동하려면 루트 디렉터리에서 다음 명령을 실행합니다.

```bash
docker compose up --build
```

컨테이너가 시작되면 API는 `http://localhost:8000` 에서 확인할 수 있습니다.
