"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { getToken } from "./api";

/** Redirects to /auth when there is no session. Returns true once a token is known to exist. */
export function useRequireAuth(): boolean {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const check = () => {
      if (getToken()) {
        setReady(true);
      } else {
        setReady(false);
        router.replace(`/auth?next=${encodeURIComponent(pathname)}`);
      }
    };
    check();
    window.addEventListener("storyforge-auth", check);
    return () => window.removeEventListener("storyforge-auth", check);
  }, [router, pathname]);

  return ready;
}
