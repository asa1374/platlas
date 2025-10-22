# platlas

Platform + Atlas. 플랫폼 지도를 그려주는 서비스.

## Backend 개발 환경

`/backend` 디렉터리에는 FastAPI 기반 API 서버와 Alembic 마이그레이션이 포함되어 있습니다.
`/frontend` 디렉터리에는 Next.js(App Router) 기반 사용자 인터페이스가 포함되어 있습니다.

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

## Frontend 개발 환경

`/frontend` 디렉터리에서 다음 명령을 실행하면 Next.js 15 기반 UI를 로컬에서 확인할 수 있습니다.

```bash
cd frontend
npm install
npm run dev
```

기본적으로 백엔드 API는 `http://localhost:8000/api/v1` 을 바라보며, 필요하면 `NEXT_PUBLIC_API_BASE_URL` 환경 변수를 통해 변경할 수 있습니다.
