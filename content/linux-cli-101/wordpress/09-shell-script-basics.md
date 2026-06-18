---
title: "바이브코딩을 위한 Linux CLI 기초 (9/10): 간단한 Shell Script"
series: linux-cli-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Linux
  - ShellScript
  - Bash
  - Automation
---

# 바이브코딩을 위한 Linux CLI 기초 (9/10): 간단한 Shell Script

이 글은 "바이브코딩을 위한 Linux CLI 기초" 시리즈의 9번째 글입니다.

---

바이브코딩에서 AI는 Shell script를 빠르게 만들어 줍니다. 그런데 많은 팀이 AI가 만들어 준 스크립트를 그대로 실행했다가 중간 단계가 실패해도 계속 진행되거나, 실행 권한이 없어 오류가 발생하거나, 공백이 포함된 파일명에서 예기치 않게 동작하는 문제를 겪습니다.

매일 아침 서버에 접속해서 같은 명령어 5개를 실행한다면, 그 5줄을 파일에 적어두고 한 번에 실행하면 됩니다. 그것이 Shell script입니다. 요리사가 레시피 없이 기억에 의존하면 실수하지만, 적어두면 누구든 같은 요리를 만들 수 있습니다.

shebang, 실행 권한, `set -e`, 인자 처리를 함께 이해해야 안전한 스크립트를 작성할 수 있습니다. AI가 만들어 준 스크립트에 이 네 가지가 갖춰져 있는지 반드시 확인해야 합니다.

shebang, 변수, 조건문, 에러 처리를 중심으로 Shell script 기초를 정리합니다.

> **핵심 인사이트:** `#!/bin/bash`와 `set -e`는 모든 스크립트에 반드시 있어야 합니다. `set -e` 없이는 중간 단계가 실패해도 스크립트가 계속 실행됩니다. 변수는 항상 `"$VAR"` 형태로 따옴표로 감싸야 공백에서 안전합니다.

## 이 글에서 다룰 문제

- 명령을 복붙하는 대신 스크립트 파일로 묶으면 무엇이 달라질까요?
- shebang, 실행 권한, 인자 처리는 왜 함께 배워야 할까요?
- `set -e`와 종료 코드는 에러 처리에 어떻게 활용될까요?
- 스크립트에서 변수와 조건문은 어디서 가장 자주 쓰일까요?
- AI가 만든 Shell script에서 확인해야 할 것은 무엇인가요?

## Shell Script 핵심 패턴

```bash
#!/bin/bash
set -e   # 어디서든 오류 발생 시 즉시 중단

# 인자 처리: 기본값 지정
NAME=${1:-"World"}   # 첫 번째 인자, 없으면 "World"
FILE=${1:?"Usage: $0 <filename>"}  # 필수 인자: 없으면 오류 메시지 출력

# 조건문: 파일/디렉터리 존재 여부
if [ -f "$FILE" ]; then
    echo "File: $FILE ($(wc -l < "$FILE") lines)"
elif [ -d "$FILE" ]; then
    echo "Directory: $FILE"
else
    echo "Not found: $FILE"
    exit 1
fi
```

```bash
#!/bin/bash
set -e

# 배포 스크립트 예시: 수동 4단계를 자동화
BACKUP_DIR="/tmp/backup-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

for file in *.sh; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        echo "Backed up: $file"
    fi
done

# 종료 코드 활용
python -m pytest tests/ 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Tests passed. Deploying..."
else
    echo "Tests failed. Aborting."
    exit 1
fi
```

## 변경 전후 비교

**Before: 수동 배포**
```text
1. SSH 접속
2. cd /opt/app
3. git pull          ← 잊어버림
4. pip install -r requirements.txt
5. systemctl restart app
→ 3단계 생략으로 구버전이 계속 실행됨
```

**After: 스크립트 배포**
```bash
#!/bin/bash
set -e
cd /opt/app
git pull
pip install -r requirements.txt
sudo systemctl restart app
echo "Deploy complete at $(date)"
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| shebang 없음 | 어떤 Shell로 실행될지 불확실 | 첫 줄에 `#!/bin/bash` 추가 |
| `set -e` 없음 | 중간 실패해도 스크립트 계속 실행 | 두 번째 줄에 `set -e` 추가 |
| 변수 따옴표 없음 | 공백 포함 파일명에서 오작동 | `"$VAR"` 형태로 항상 따옴표 |
| 실행 권한 없음 | `Permission denied` 오류 | `chmod u+x script.sh` |
| 에러 무시하고 진행 | 이전 단계 실패 후 잘못된 상태로 계속 | `set -e` 또는 명시적 에러 체크 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"Python 프로젝트 배포 Shell script를 만들어줘.
git pull → pip install → 테스트 실행 → 서비스 재시작 순서,
각 단계 실패 시 즉시 중단,
실행 시 날짜와 단계를 출력,
환경(dev/prod) 인자로 구분"

# AI 결과물 검증 체크포인트:
# - 첫 줄에 #!/bin/bash가 있는가?
# - set -e 또는 명시적 에러 처리가 있는가?
# - 변수가 "$VAR" 형태로 따옴표로 감싸져 있는가?
# - chmod u+x 실행 권한이 설명되어 있는가?
# - 민감 정보(비밀번호 등)가 스크립트에 하드코딩되지 않았는가?
```

## 운영 체크리스트

- [ ] 모든 스크립트에 `#!/bin/bash` shebang이 있다
- [ ] `set -e`로 에러 발생 시 즉시 중단한다
- [ ] 변수를 `"$VAR"` 형태로 따옴표로 감싼다
- [ ] `chmod u+x`로 실행 권한을 부여했다
- [ ] 중요 스크립트는 버전 관리(Git)에 포함된다

## 처음 질문으로 돌아가기

- **shebang이란?** 스크립트 첫 줄의 `#!/bin/bash`로, 이 파일을 실행할 인터프리터를 지정합니다. 없으면 현재 Shell 종류에 따라 다르게 실행될 수 있습니다.
- **`set -e`가 중요한 이유는?** 기본적으로 Shell은 명령이 실패해도 다음 줄을 계속 실행합니다. `set -e`는 어디서든 오류가 나면 즉시 중단해 잘못된 상태가 계속되는 것을 막습니다.
- **변수에 따옴표를 써야 하는 이유는?** `$FILE`이 `my file.txt`처럼 공백을 포함하면 `"$FILE"` 없이는 `my`와 `file.txt` 두 개의 인자로 분리됩니다. 항상 `"$VAR"` 형태로 감싸야 안전합니다.

## 정리

바이브코딩에서 AI가 만들어 준 Shell script에서 shebang, `set -e`, 변수 따옴표, 실행 권한을 반드시 확인하세요. 스크립트는 반복 작업을 자동화하고 실수를 줄이는 강력한 도구입니다. 다음 글에서는 SSH와 원격 서버 접속을 다룹니다.

## 참고 자료

- [GNU Bash Manual](https://www.gnu.org/software/bash/manual/bash.html)
- [ShellCheck — Shell script 정적 분석 도구](https://www.shellcheck.net/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Linux CLI 기초 (1/10): Linux와 CLI란?
- 바이브코딩을 위한 Linux CLI 기초 (2/10): 파일 시스템 탐색
- 바이브코딩을 위한 Linux CLI 기초 (3/10): 파일 조작
- 바이브코딩을 위한 Linux CLI 기초 (4/10): 텍스트 처리
- 바이브코딩을 위한 Linux CLI 기초 (5/10): 프로세스 관리
- 바이브코딩을 위한 Linux CLI 기초 (6/10): 파일 권한과 소유자
- 바이브코딩을 위한 Linux CLI 기초 (7/10): 파이프와 리다이렉션
- 바이브코딩을 위한 Linux CLI 기초 (8/10): 환경변수와 PATH
- **바이브코딩을 위한 Linux CLI 기초 (9/10): 간단한 Shell Script (현재 글)**
- 바이브코딩을 위한 Linux CLI 기초 (10/10): SSH와 원격 서버 접속
<!-- toc:end -->

Tags: 바이브코딩, Linux, ShellScript, Bash, Automation
