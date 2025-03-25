퀴즈 API 서버

``` 예시는 API Docs 참고해주시길 바랍니다.
실행 전 CREATE_TABLE.sql 실행해주시길 바랍니다.

실행 방법

```bash
uvicorn router.router:app --host 0.0.0.0 --port 8000
```

## 데이터베이스 연결 관리

이 프로젝트는 `DBSessionManager` 클래스를 사용하여 비동기 DB 세션을 효율적으로 관리합니다.

### DBManager 소개

`DBSessionManager`는 비동기 데이터베이스 세션을 관리하기 위한 전용 클래스입니다. 이 클래스는 다음과 같은 기능을 제공합니다:

- 비동기 데이터베이스 연결 생성 및 관리
- 세션 풀 관리를 통한 효율적인 리소스 사용
- 트랜잭션 관리 자동화 
- 데이터베이스 연결 에러 처리
## 이를 통해 API 요청시 마다 DB 세션관리가 용이하게 됩니다.

### 사용 방법

```python
from db.manager import DBManager

# DBManager 인스턴스 생성
db_manager = DBManager()

# 비동기 컨텍스트 관리자로 사용
async with db_manager.session() as session:
    # 데이터베이스 작업 수행
    result = await session.execute(query)
    
# 의존성 주입으로 사용 (FastAPI)
async def get_db():
    async with db_manager.session() as session:
        yield session
        
# 트랜잭션 사용 예시
async with db_manager.session() as session:
    async with session.begin():
        # 트랜잭션 내에서 작업 수행
        await session.execute(query)
```

### 설정 방법

데이터베이스 연결 설정은 `config.local.toml` 파일에서 관리됩니다:

```toml
[database]
url = "postgresql+asyncpg://username:password@localhost:5432/dbname"
echo = false
pool_size = 5
max_overflow = 10
```

## 주요 기능들

## 1. 퀴즈 생성
## 2. 퀴즈 수정
## 3. 퀴즈 삭제
## 4. 퀴즈 목록 조회
## 5. 퀴즈 상세 조회
## 6. 퀴즈 응시 시작
## 7. 퀴즈 응시 상태 조회
## 8. 퀴즈 답안 저장
## 9. 퀴즈 답안 제출

