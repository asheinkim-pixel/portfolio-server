================================
🔧 배포 실패 해결 완료!
================================

## 🐛 문제 원인

```
"Exited with status 1 while running your code"
→ 서버 시작 실패
```

**원인: 포트 설정 오류**
- Render.com은 환경변수 PORT를 제공
- 기존 코드는 포트 5000으로 하드코딩
- 충돌 발생!

---

## ✅ 해결 완료!

### 수정된 파일 3개:

**1. server.py**
```python
# 추가됨
import os

# 변경됨
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port, debug=False)
```

**2. Procfile**
```
web: gunicorn server:app --bind 0.0.0.0:$PORT
```

**3. render.yaml**
```yaml
startCommand: gunicorn server:app --bind 0.0.0.0:$PORT
```

---

## 🚀 다시 배포하기

### 방법 1: GitHub 업데이트 (권장)

```
1. GitHub 접속
2. portfolio-server repository
3. 수정된 파일 3개 교체:
   - server.py (새 버전)
   - Procfile (새 버전)
   - render.yaml (새 버전)
4. Commit changes
5. Render가 자동으로 재배포!
```

### 방법 2: Render에서 수동 재배포

```
1. Render Dashboard
2. portfolio-server 클릭
3. "Manual Deploy" 클릭
4. "Clear build cache & deploy"
5. 3-5분 대기
```

---

## 📋 배포 체크리스트

### 필수 파일 (모두 업데이트!)
□ server.py (수정됨 ✅)
□ portfolio.html
□ requirements.txt
□ Procfile (수정됨 ✅)
□ render.yaml (수정됨 ✅)

### GitHub에 올리기
□ 5개 파일 모두 최신 버전
□ Commit 완료
□ Repository 확인

### Render 배포
□ 자동 배포 시작 확인
□ Logs 탭에서 진행 상황 확인
□ "Live" 상태 되면 성공!

---

## 🔍 배포 진행 확인

### Render Logs 보기
```
1. Render Dashboard
2. portfolio-server 클릭
3. "Logs" 탭
4. 실시간 로그 확인
```

### 성공 메시지
```
✅ "Build succeeded"
✅ "Starting service..."
✅ "🚀 실시간 주가 서버 시작!"
✅ "Your service is live"
```

### 실패하면
```
❌ "Exited with status 1"
→ Logs에서 에러 메시지 확인
→ 파일 내용 재확인
```

---

## 💡 일반적인 에러들

### 에러 1: Module not found
```
원인: requirements.txt 누락
해결: requirements.txt 확인
```

### 에러 2: Port binding failed
```
원인: 포트 설정 문제
해결: 위에서 이미 해결됨! ✅
```

### 에러 3: Import error
```
원인: 파일명 오타
해결: server.py 파일명 확인
```

### 에러 4: Syntax error
```
원인: Python 코드 오류
해결: server.py 코드 확인
```

---

## 🎯 배포 후 확인

### 1. URL 접속
```
https://your-app-name.onrender.com

→ 20초 정도 대기 (첫 시작)
→ "Your service is live" 확인
```

### 2. API 테스트
```
https://your-app-name.onrender.com/health

→ {"status": "ok"} 나오면 성공!
```

### 3. 포트폴리오 접속
```
https://your-app-name.onrender.com/portfolio.html

→ 종목 추가
→ 실시간 데이터 확인
→ 완료! 🎉
```

---

## ⚠️ Render 무료 플랜 특징

```
"Your free instance will spin down with inactivity"
→ 15분 미사용 시 슬립 모드
→ 다시 접속하면 50초 안에 깨어남
→ 정상적인 동작입니다!

해결:
- 자주 사용하면 문제 없음
- UptimeRobot으로 5분마다 핑
  (https://uptimerobot.com)
```

---

## 📝 파일 내용 확인

### server.py (중요 부분)
```python
import os  # 이거 있어야 함!

# 마지막 부분
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### Procfile
```
web: gunicorn server:app --bind 0.0.0.0:$PORT
```

### render.yaml
```yaml
startCommand: gunicorn server:app --bind 0.0.0.0:$PORT
```

---

## 🔄 업데이트 순서

```
1. 수정된 파일 3개 다운로드
2. GitHub에 업로드 (교체)
3. Render 자동 재배포 (3-5분)
4. 완료!
```

---

## 🆘 여전히 실패하면

### 확인 사항:
□ server.py에 `import os` 있나요?
□ Procfile에 `--bind 0.0.0.0:$PORT` 있나요?
□ 파일명이 정확한가요? (대소문자)
□ GitHub에 모든 파일 있나요?

### Logs에서 찾을 것:
```
- "ModuleNotFoundError" → requirements.txt
- "SyntaxError" → server.py 코드
- "Port binding" → 포트 설정
- "File not found" → 파일명/경로
```

---

## ✅ 해결 완료!

```
수정된 파일 3개를 다운로드하고
GitHub에 업로드하면
자동으로 재배포됩니다!

3-5분 후 정상 작동! 🎉
```

================================
문제 해결됨! 다시 배포하세요!
================================
