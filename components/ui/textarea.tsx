import type { TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/class-names";

export type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label?: string;
  helperText?: string;
  error?: string;
};

export function Textarea({ className, error, helperText, label, ...props }: TextareaProps) {
  const control = (
    <textarea
      aria-invalid={error ? "true" : undefined}
      className={cn("textarea", className)}
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
