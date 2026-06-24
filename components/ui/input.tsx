import type { InputHTMLAttributes } from "react";
import { cn } from "@/lib/class-names";

export type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  helperText?: string;
  error?: string;
};

export function Input({ className, error, helperText, label, ...props }: InputProps) {
  const control = (
    <input
      aria-invalid={error ? "true" : undefined}
      className={cn("input", className)}
      {...props}
    />
  );

  if (!label && !helperText && !error) {
    return control;
  }

  return (
    <label className="field">
      {label ? <span className="field__label">{label}</span> : null}
      {control}
      {error ? <p className="field__error">{error}</p> : null}
      {!error && helperText ? <p className="field__helper">{helperText}</p> : null}
    </label>
  );
}
