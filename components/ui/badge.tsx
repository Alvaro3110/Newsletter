import type { HTMLAttributes } from "react";
import { cn } from "@/lib/class-names";

export type BadgeTone = "neutral" | "success" | "warning" | "info" | "danger";

export type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: BadgeTone;
};

export function Badge({ className, tone = "neutral", ...props }: BadgeProps) {
  return <span className={cn("badge", `badge--${tone}`, className)} {...props} />;
}
