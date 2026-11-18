/**
 * Client thread ids. docs/api.md requires 8 to 64 characters using letters,
 * digits, underscore and hyphen. The server still builds the effective thread
 * id from role and this value, so roles never share history.
 */

const THREAD_ID_PATTERN = /^[A-Za-z0-9_-]{8,64}$/;

export function createThreadId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  const random = Math.random().toString(36).slice(2, 10);
  return `thread-${Date.now().toString(36)}-${random}`;
}

export function isValidThreadId(value: string): boolean {
  return THREAD_ID_PATTERN.test(value);
}
