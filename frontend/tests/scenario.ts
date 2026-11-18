import {
  contractFixtureResponses,
  type ContractFixtureKey,
} from "@/lib/fixtures";

/**
 * Returns one of Lane A's frozen contract responses by its fixture key, so
 * tests never restate fixture text.
 */
export function scenario(id: ContractFixtureKey) {
  return {
    id,
    response: contractFixtureResponses[id],
  };
}
