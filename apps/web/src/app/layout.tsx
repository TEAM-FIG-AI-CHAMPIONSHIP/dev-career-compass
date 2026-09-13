import type { Metadata } from "next";
import { IBM_Plex_Sans_KR, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

// subsets는 preload 대상만 고릅니다. next/font가 받아오는 Google CSS에는
// 한글 슬라이스도 들어 있어 self-host되며, 필요한 순간에 로드됩니다.
const plexKR = IBM_Plex_Sans_KR({
  variable: "--font-plex-kr",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  display: "swap",
});

/**
 * 첫 페인트 전에 저장된 테마를 붙입니다.
 *
 * 이 줄이 없으면 다크를 고른 사람에게 흰 화면이 한 번 번쩍입니다. 저장된 값이
 * 없으면 아무것도 붙이지 않고 운영체제 설정(prefers-color-scheme)에 맡깁니다.
 */
const THEME_INIT = `(function(){try{var t=localStorage.getItem("rm-theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}catch(e){}})()`;

export const metadata: Metadata = {
  title: {
    default: "Refactor.me",
    template: "%s · Refactor.me",
  },
  description:
    "기업 기술 블로그와 뉴스, 채용 공고를 분석해 지금 만들 프로젝트를 근거와 함께 제안합니다.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="ko"
      className={`${plexKR.variable} ${plexMono.variable} h-full`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT }} />
      </head>
      <body className="flex min-h-full flex-col">{children}</body>
    </html>
  );
}
