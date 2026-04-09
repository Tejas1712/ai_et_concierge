"use client";

interface AlphaAvatarProps {
  persona?: string; // "student" | "trader" | "professional" | "conservative" | "default"
  size?: number;
  showName?: boolean;
}

// Maps persona type to a unique DiceBear seed
// Each seed generates a completely different avatar
function getAvatarSeed(persona: string): string {
  const seeds: Record<string, string> = {
    student:      "alphaassist-student",
    trader:       "alphaassist-trader",
    professional: "alphaassist-professional",
    conservative: "alphaassist-conservative",
    default:      "alphaassist-default",
  };
  return seeds[persona] ?? seeds.default;
}

// Maps persona type to a background color
function getAvatarBg(persona: string): string {
  const colors: Record<string, string> = {
    student:      "b6e3f4", // light blue - fresh & youthful
    trader:       "ff6b6b", // red - aggressive & energetic
    professional: "1a1a2e", // dark navy - authoritative
    conservative: "c8e6c9", // soft green - calm & safe
    default:      "d4a843", // ET gold - brand color
  };
  return colors[persona] ?? colors.default;
}

export function getPersonaType(
  careerStage?: string,
  riskAppetite?: string,
  background?: string
): string {
  const stage = (careerStage ?? "").toLowerCase();
  const risk = (riskAppetite ?? "").toLowerCase();
  const bg = (background ?? "").toLowerCase();

  if (stage.includes("student") || stage.includes("early") || stage.includes("fresher")) {
    return "student";
  }
  if (risk === "aggressive" || bg.includes("trader") || bg.includes("broker")) {
    return "trader";
  }
  if (risk === "conservative" || stage.includes("retire")) {
    return "conservative";
  }
  if (bg.includes("engineer") || bg.includes("manager") || bg.includes("executive") || bg.includes("professional")) {
    return "professional";
  }
  return "default";
}

export default function AlphaAvatar({ persona = "default", size = 48, showName = false }: AlphaAvatarProps) {
  const seed = getAvatarSeed(persona);
  const bg = getAvatarBg(persona);
  const avatarUrl = `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}&backgroundColor=${bg}&radius=50`;

  return (
    <div className="alpha-avatar-wrapper" style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
      <img
        src={avatarUrl}
        alt="AlphaAssist Avatar"
        width={size}
        height={size}
        style={{
          borderRadius: "50%",
          border: "2px solid #d4a843",
          background: `#${bg}`,
          flexShrink: 0,
        }}
      />
      {showName && (
        <span style={{ fontSize: 11, fontWeight: 600, color: "#d4a843", letterSpacing: "0.5px" }}>
          AlphaAssist
        </span>
      )}
    </div>
  );
}
