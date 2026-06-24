import type { HTMLAttributes } from "react";
import { cn } from "@/lib/class-names";

export type CardProps = HTMLAttributes<HTMLDivElement>;
export type CardTitleProps = HTMLAttributes<HTMLHeadingElement>;

export function Card({ className, ...props }: CardProps) {
  return <div className={cn("card", className)} {...props} />;
}

export function CardHeader({ className, ...props }: CardProps) {
  return <div className={cn("card__header", className)} {...props} />;
}

export function CardTitle({ className, ...props }: CardTitleProps) {
  return <h3 className={cn("card__title", className)} {...props} />;
}

export function CardContent({ className, ...props }: CardProps) {
  return <div className={cn("card__content", className)} {...props} />;
}
