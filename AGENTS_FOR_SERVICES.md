
* 각 서비스에 copilot-instruction.md 로 배포할 공통 지침을 작성한다.

## 문서작성지침
* 초기설정방법 등 상세한 내용은 기술할 필요없이 필수 적용 지침만 간단히 기술
* 멀티라인의 코드예시 포함하지말것

# 필요한 사항
1. sturctured logging 적용지침,
2. audit logging 에 적용지침
3. mysingle package 의 cicd 적용지침
4. Proto 패키지 cicd 특별적용지침
  * grpc 서버를 제공하는 서비스에서 자신의 proto 파일을 업데이트시 (e.g strategy 레포에서 strategy_servcie.proto 의 변경 시)
  * 컨슈머 서비스에서 서버의 proto 변경요청시의 지침 (e.g backtest-service 레포에서 strategy_servcie.proto 의 rpc 추가요청 시)
5. api 엔드포인트 구성시 인증 구성지침
  * user객체 또는 user_id 를 참조하는 엔드포인트 구성지침
  * 일반 protected api 엔드포인트 구성지침
  * 그밖의 필요사항
6.
