/** Built-in demo analysis used whenever the backend or Hindsight cannot be reached, so the Memory Lab always shows a result. */
export const fallbackBaseline =
  'Based only on the current feedback, customers appear to be struggling to find delivery and promo details during mobile checkout. The immediate signal suggests navigation or information architecture friction, but current feedback alone cannot establish whether this is a recurrence of an older problem.';

export const fallbackHistorical =
  'Hindsight changes the interpretation: the current complaint matches a known mobile checkout problem first detected in January. Navigation simplification improved desktop complaints by 61% while mobile friction persisted; a later mobile redesign was followed by renewed complaints. TRACE should investigate whether the redesigned mobile navigation reintroduced the earlier scanning problem rather than treating this as a brand-new issue.';

export const fallbackMemories: string[] = [
  'Mobile checkout confusion was first detected in January 2026 among support and app-review signals.',
  'Navigation simplification shipped in March 2026. Desktop complaints fell 61%, while mobile complaints persisted.',
  'A sticky order summary later reduced desktop drop-offs but did not resolve mobile scanning difficulty.',
  'A compact mobile checkout redesign shipped in July 2026 with a new summary drawer.',
  'Mobile complaints rose again in August, concentrated among Android users.',
  'September feedback again reports difficulty finding delivery and promo details before payment.',
];

export const fallbackImpact: string[] = [
  'Investigate the mobile navigation and information hierarchy before proposing another copy-only fix.',
  'Compare Android behavior with the March desktop improvement instead of assuming the prior intervention solved the full problem.',
  'Reuse the measured history: the previous navigation change improved desktop complaints but did not resolve mobile scanning difficulty.',
];
