"use client";

import { useState } from "react";
import { CheckOption, LevelOption } from "@/components/ui/CheckOption";
import { RepoField } from "@/components/ui/RepoField";
import { JobButton } from "@/components/ui/Button";

export function InteractiveSamples() {
  const [checked, setChecked] = useState<Record<string, boolean>>({ api: true });
  const [level, setLevel] = useState("deployed");
  const [repo, setRepo] = useState("jiwon-k/order-api");
  const [job, setJob] = useState("backend");

  const toggle = (id: string) => (next: boolean) =>
    setChecked((prev) => ({ ...prev, [id]: next }));

  return (
    <div className="grid grid-cols-1 gap-7 lg:grid-cols-2">
      <div className="flex flex-col gap-2.5">
        <p className="font-mono text-[0.71875rem] text-ink-muted">
          CheckOption — 눌러보세요
        </p>
        <CheckOption
          label="게시판·쇼핑몰 같은 CRUD 서비스"
          checked={!!checked.crud}
          onChange={toggle("crud")}
        />
        <CheckOption
          label="외부 API를 붙인 서비스"
          description="결제, 지도, 소셜 로그인 등"
          checked={!!checked.api}
          onChange={toggle("api")}
        />
        <CheckOption
          label="배포까지 해서 남이 써 봤다"
          description="도메인이나 URL로 접근 가능한 상태"
          checked={!!checked.deploy}
          onChange={toggle("deploy")}
        />
      </div>

      <div className="flex flex-col gap-2.5">
        <p className="font-mono text-[0.71875rem] text-ink-muted">
          RepoField — 기본 / 오류
        </p>
        <RepoField value={repo} onChange={setRepo} />
        <RepoField
          value="jiwon-k/private-lab"
          onChange={() => {}}
          error="읽을 수 없는 저장소입니다. 이 항목은 빼고 선택하신 내용만으로 진행합니다."
        />
        <p className="mt-3 font-mono text-[0.71875rem] text-ink-muted">
          JobButton — 하나만 선택
        </p>
        <div className="flex flex-wrap gap-2.5">
          {[
            ["backend", "서버·백엔드"],
            ["frontend", "웹 프론트엔드"],
            ["data", "데이터·AI"],
          ].map(([id, label]) => (
            <JobButton
              key={id}
              selected={job === id}
              onClick={() => setJob(id)}
            >
              {label}
            </JobButton>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-2.5 lg:col-span-2">
        <p className="font-mono text-[0.71875rem] text-ink-muted">
          LevelOption — 진행 수준, 하나만 선택
        </p>
        <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-3">
          {[
            ["ran", "STEP 1", "돌아가는 것까지", "로컬에서 기능이 동작합니다"],
            ["deployed", "STEP 2", "배포까지", "남이 접속해 써볼 수 있습니다"],
            [
              "fixed",
              "STEP 3",
              "문제를 만나 고치는 것까지",
              "터진 것을 찾아 고치고 기록을 남겼습니다",
            ],
          ].map(([id, step, title, desc]) => (
            <LevelOption
              key={id}
              step={step}
              title={title}
              description={desc}
              selected={level === id}
              onSelect={() => setLevel(id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
