import { createContext, useContext, useEffect, useMemo, useState } from "react";
import liff from "@line/liff";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [isReady, setIsReady] = useState(false);
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const liffId = import.meta.env.VITE_LINE_LIFF_ID;
    if (!liffId || liffId === "your-liff-id") {
      const localProfile = {
        userId: localStorage.getItem("marketAppUserId") || "local-line-user",
        displayName: "本機測試使用者",
      };
      localStorage.setItem("marketAppUserId", localProfile.userId);
      setProfile(localProfile);
      setIsReady(true);
      return;
    }

    liff
      .init({ liffId })
      .then(async () => {
        setIsReady(true);
        if (liff.isLoggedIn()) {
          const nextProfile = await liff.getProfile();
          localStorage.setItem("marketAppUserId", nextProfile.userId);
          setProfile(nextProfile);
        }
      })
      .catch(() => setIsReady(true));
  }, []);

  const value = useMemo(
    () => ({
      isReady,
      profile,
      login: () => {
        if (liff.isInClient() || import.meta.env.VITE_LINE_LIFF_ID) {
          liff.login();
        }
      },
      logout: () => {
        if (liff.isLoggedIn()) {
          liff.logout();
        }
        localStorage.removeItem("marketAppUserId");
        setProfile(null);
      },
    }),
    [isReady, profile]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
