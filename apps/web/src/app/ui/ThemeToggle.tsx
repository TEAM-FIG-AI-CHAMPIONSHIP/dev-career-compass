"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";

/** 갤러리에서 라이트/다크를 바꿔 보기 위한 것입니다. 제품 화면에는 없습니다. */
export function ThemeToggle() {
  const [theme, setTheme] = useState<"system" | "light" | "dark">("system");

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", theme);
  }, [theme]);

  return (
    <div className="flex items-center gap-2">
      {(["system", "light", "dark"] as const).map((t) => (
        <Button
          key={t}
          variant={theme === t ? "primary" : "secondary"}
          onClick={() => setTheme(t)}
          className="px-3.5 py-2.5 text-[0.8125rem]"
        >
          {t === "system" ? "시스템" : t === "light" ? "라이트" : "다크"}
        </Button>
      ))}
    </div>
  );
}
