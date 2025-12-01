# 프런트엔드 인증 개발 가이드 (Next.js + HeyAPI)

본 패키지와 호환되는 Next.js 프런트엔드 인증 구성을 설명합니다. FastAPI 백엔드의 OpenAPI 스펙으로 HeyAPI SDK를 생성하여 사용하며, Kong Gateway 경유로 호출합니다.

## 전제
- Kong External 라우트에 `jwt` 플러그인 활성화 (/strategy, /iam 등)
- 브라우저 요청은 쿠키를 포함하여 전달(CORS `credentials: true`)
- 사용자 토큰은 `access_token` 쿠키로 관리하며, 요청 시 `Authorization: Bearer` 헤더를 자동 추가

## 환경 변수
- `NEXT_PUBLIC_API_GATEWAY_URL` (예: `http://localhost:8000` 또는 운영 게이트웨이 URL)
  - 서비스별 SDK는 `${NEXT_PUBLIC_API_GATEWAY_URL}/{service}`로 접근합니다.

## SDK 생성 설정(예시)
`src/clients/strategy/openapi-ts.config.ts`
```ts
import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "./src/clients/strategy/openapi.json",
  output: {
    format: "prettier",
    path: "./src/clients/strategy/client",
  },
  plugins: [
    "@hey-api/schemas",
    { name: "@hey-api/client-next", exportFromIndex: true, runtimeConfigPath: "../runtimeConfig" },
    { name: "@hey-api/transformers" },
    {
      name: "@hey-api/sdk",
      asClass: true,
      classNameBuilder: "{{name}}Service",
      methodNameBuilder: (operation) => {
        let name = operation.summary;
        if (name) {
          name = name
            .toLowerCase()
            .replace(/[\s\-_]+(\w)/g, (_, c) => c.toUpperCase())
            .replace(/[\s\-_]+/g, "");
        }
        return name || "defaultMethodName";
      },
    },
  ],
});
```

## 런타임 구성(게이트웨이 + JWT 헤더)
`src/clients/strategy/runtimeConfig.ts`
```ts
import type { CreateClientConfig } from "./client";

function getAuthTokenFromCookie(): string | null {
  if (typeof window === "undefined") return null;
  const cookies = document.cookie.split(";");
  const c = cookies.find((cookie) => cookie.trim().startsWith("access_token="));
  if (!c) return null;
  const token = c.split("=")[1];
  return token && token !== "" ? token : null;
}

export const createClientConfig: CreateClientConfig = (config) => {
  const baseConfig = {
    ...config,
    baseUrl: process.env.NEXT_PUBLIC_API_GATEWAY_URL
      ? `${process.env.NEXT_PUBLIC_API_GATEWAY_URL}/strategy`
      : "http://localhost:8003",
    credentials: "include" as const,
  };

  if (typeof window !== "undefined") {
    const token = getAuthTokenFromCookie();
    if (token) {
      baseConfig.headers = {
        ...baseConfig.headers,
        Authorization: `Bearer ${token}`,
      };
    }
  }

  return baseConfig;
};
```
- 게이트웨이 프리픽스(`/strategy`)는 Kong 라우트와 일치해야 합니다.
- `credentials: "include"`로 쿠키가 항상 전송됩니다.
- 브라우저에서 읽을 수 있는 쿠키 전략(보안/편의 트레이드오프)을 사용합니다. 고보안이 필요하면 SSR 또는 API Route에서 서버 측에서 `Authorization` 헤더를 주입하세요.

## 사용 예시
```ts
// 예: pages 또는 app 라우트의 클라이언트 컴포넌트에서
import { StrategyService } from "@/clients/strategy/client";

export async function loadMyStrategies() {
  const api = new StrategyService();
  const res = await api.listMyStrategies({ page: 1, size: 20 });
  return res.data;
}
```

요청 단위로 헤더 덮어쓰기:
```ts
const api = new StrategyService({ headers: { "Idempotency-Key": crypto.randomUUID() } });
```

SSR/서버 환경에서의 헤더 주입(개략):
```ts
// Next.js Route Handler (app/api/*)에서
import { cookies } from "next/headers";
import { StrategyService } from "@/clients/strategy/client";

export async function GET() {
  const access = cookies().get("access_token")?.value;
  const api = new StrategyService({
    headers: access ? { Authorization: `Bearer ${access}` } : {},
    baseUrl: `${process.env.NEXT_PUBLIC_API_GATEWAY_URL}/strategy`,
    credentials: "include",
  });
  const res = await api.listMyStrategies({ page: 1, size: 10 });
  return Response.json(res.data, { status: 200 });
}
```

## 인증 흐름
1. 로그인: IAM 서비스(`/iam`)에 인증 → 서버가 `access_token` 쿠키 설정
2. SDK 호출: 런타임 설정이 쿠키에서 토큰을 읽어 `Authorization: Bearer` 헤더 추가
3. Kong: `jwt` 플러그인이 토큰 검증 후 업스트림 서비스로 전달
4. 백엔드: 미들웨어가 `request.state.user` 주입 → 의존성(`get_current_user`)으로 보호

## 오류 처리/관찰성
- 401 발생 시 로그인 페이지로 리디렉션
- 응답 헤더의 `Correlation-Id`를 캡처하여 오류 리포팅/로깅에 포함

## CORS 주의사항
- 게이트웨이에 프런트 도메인이 `origins`에 등록되어야 합니다.
- `credentials: true` 및 `Authorization`, `Correlation-Id` 헤더 노출 필요

## 로컬 테스트 체크리스트
- [ ] `GET ${NEXT_PUBLIC_API_GATEWAY_URL}/strategy/health` → 200
- [ ] 무토큰으로 `/strategy/me` → 401
- [ ] 로그인 후 `/strategy/me` → 200
- [ ] 응답에 `Correlation-Id` 있음
