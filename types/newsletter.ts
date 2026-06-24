export type NewsletterStatus =
  | "approved"
  | "draft"
  | "failed"
  | "generating"
  | "queued"
  | "review"
  | "scheduled"
  | "sent";

export type NewsletterSummary = {
  id: string;
  title: string;
  audience: string;
  owner: string;
  progress: number;
  status: NewsletterStatus;
  updatedAt: string;
};

export type ReviewQueueItem = {
  id: string;
  title: string;
  note: string;
  status: NewsletterStatus;
};

export type NewsletterDraftInput = {
  title: string;
  audience: string;
  context: string;
  sources?: string[];
};
