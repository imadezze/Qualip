export const GREETING_MESSAGES = ["How can CertiBot help you today?", "Ready to check your Qualiopi compliance."];

export function getRandomGreeting(): string {
  return GREETING_MESSAGES[
    Math.floor(Math.random() * GREETING_MESSAGES.length)
  ] as string;
}
