import { describe, expect, it } from "vitest";
import { contractFixtureResponses } from "@/lib/fixtures";
import snapshot from "./contract-fixtures.snapshot.json";

/**
 * contract-fixtures.snapshot.json was generated from Lane A's source, not
 * written by hand:
 *
 *   backend\.venv\Scripts\python.exe -B -c "import json,sys; sys.path.insert(0,'backend/tests/api'); from contract_fixtures import contract_response_fixtures; print(json.dumps(contract_response_fixtures(), indent=2, sort_keys=True))"
 *
 * This test fails if the frontend fixtures drift from the frozen backend
 * fixtures. Regenerate the snapshot only when Lane A changes them.
 */
describe("contract fixture parity", () => {
  it("matches Lane A's fixtures value for value", () => {
    expect(contractFixtureResponses).toEqual(snapshot);
  });

  it("holds one response per status and presentation pair", () => {
    expect(Object.keys(contractFixtureResponses)).toHaveLength(15);
    expect(Object.keys(snapshot)).toHaveLength(15);
  });
});
