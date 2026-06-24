import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/class-names";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type ButtonSize = "sm" | "md" | "lg";

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

export function Button({
  className,
  variant = "primary",
  size = "md",
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn("button", `button--${variant}`, size !== "md" && `button--${size}`, className)}
      type={type}
      {...props}
    />
  );
}
