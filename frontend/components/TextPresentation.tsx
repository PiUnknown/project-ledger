/**
 * Text presentation. The contract supplies the answer text for every status,
 * so this renderer prints exactly what the response carried.
 */
export function TextPresentation({ text }: { text: string }) {
  return <p className="answer-body">{text}</p>;
}
