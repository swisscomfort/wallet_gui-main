"""Agent that filters mnemonic candidates from content hits."""

from __future__ import annotations

import re
import time

from .base import Agent, Result, Task

BIP39 = set(
    "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve "
    "acid acoustic acquire across act action actor actress actual adapt add addict address adjust admit adult "
    "advance advice aerobic affair afford afraid again age agent agree ahead aim air airport aisle alarm album "
    "alcohol alert alien all alley allow almost alone alpha already also alter always amateur amazing among amount "
    "amused analyst anchor ancient anger angle angry animal ankle announce annual another answer antenna antique "
    "anxiety any apart apology appear apple approve april arch arctic area arena argue arm armed armor army around "
    "arrange arrest arrive arrow art artefact artist artwork ask aspect assault asset assist assume asthma athlete atom "
    "attack attend attitude attract auction audit august aunt author auto autumn average avocado avoid awake aware away "
    "awesome awful awkward axis baby bachelor bacon badge bag balance balcony ball bamboo banana banner bar barely bargain "
    "barrel base basic basket battle beach bean beauty because become beef before begin behave behind believe below belt bench "
    "benefit best betray better between beyond bicycle bid bike bind biology bird birth bitter black blade blame blanket blast "
    "bleak bless blind blood blossom blouse blue blur blush board boat body boil bomb bone bonus book boost border boring borrow "
    "boss bottom bounce box boy bracket brain brand brass brave bread breeze brick bridge brief bright bring brisk broccoli "
    "broken bronze broom brother brown brush bubble buddy budget buffalo build bulb bulk bullet bundle bunker burden burger burst "
    "bus business busy butter buyer buzz".split()
)


def maybe_mnemonic(text: str) -> tuple[bool, str]:
    words = [w for w in re.findall(r"[a-z]{3,}", text.lower()) if w in BIP39]
    for size in (24, 21, 18, 15, 12):
        for idx in range(0, max(0, len(words) - size + 1)):
            chunk = words[idx : idx + size]
            if len(chunk) == size:
                return True, " ".join(chunk[:size])
    return False, ""


class MnemonicValidateAgent(Agent):
    NAME = "mnemonic_validate"

    def run(self, task: Task) -> Result:
        t0 = time.time()
        hits = task.payload.get("hits", [])
        mnemonics: list[dict[str, object]] = []
        for hit in hits:
            ok, phrase = maybe_mnemonic(str(hit.get("snippet", "")))
            if ok:
                mnemonics.append(
                    {
                        "file": hit.get("file"),
                        "line": hit.get("line"),
                        "mnemonic": phrase,
                    }
                )
        return Result(kind=self.NAME, ok=True, data={"mnemonics": mnemonics}, took_s=time.time() - t0)

