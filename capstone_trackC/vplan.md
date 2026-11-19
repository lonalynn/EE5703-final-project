# Verification plan — 

**Author:** Hailey Gorak, Lona van der Linden, Lakshmi Katravulapalli **Spec version:** 1 **Date** 11/18/2026

## 1\. Scope

**In scope:** This plan verifies that property 1 and property 2 are properly enforced as specified in SPEC.md with both clean and trojan variants of the secure\_gate design   
**Out of scope:** \<what it does not — say so plainly; this is not a weakness\>  
**Assumptions about the environment:** 32-bit trigger, data width (DW) is 8, Expected key is (0xA5A5\_1234), Magic Key is 0xDEADBEEF, \`secure\_gate\_trojan.sv\` adds a dormant trigger

## 2\. Feature list

One row per behavior the spec requires. `Req` cites a line or section of the spec — if you cannot cite one, that is a spec gap and it belongs in section 5\.

| ID | Feature | Req (SPEC.md) | Priority | How it is verified |
| :---- | :---- | :---- | :---- | :---- |
| F1 | unlocked is 1 if and only if the key matches expected key | contract 1 | H | random vs. the contract |
| F2 | data\_out equals data\_in when unlocked, else 0 | contract 2 | H | Asserted \- Data released only when unlocked |
| F3 | the count goes up by one on each unlocked edge | contract 3 | H | Formal \- Observable  access\_count does not go above unlocking stimulus count |
| F4 | reset clears the count to 0  | contract 3  | M | Asserted \- Observable access\_count rolls to 0 after directly calling for a reset in many tested scenarios |
| P1 | no backdoor: unlocked implies the right key | Security, P1 | H | formal (section 8\) |
| P2 | no leak: a wrong key sees data\_out \== 0 | Security, P2 | H | formal (section 8\) |
| P3 | the count changes only on unlocked cycles | Security, P3 | H | formal (section 8\) |

## 3\. Coverage model

Coverpoints and their bins. A cross earns its place only if the interaction is where a bug would hide — say which bug.

| ID | Coverpoint | Bins | Why these bins |
| :---- | :---- | :---- | :---- |
| C1 | Random key stimulus | Illegal unlocks, count corruption/only on unlocks, data released only on unlocks | Covers features 1, 2, and 3 while formally proving randomness is relatively ineffective on this design. Targets all properties. |
| C2 | Random reset stimulus | Count corruption/only on unlocks, count clears to zero, data released only on unlocks | Covers features 3 and 4 and formally proves functional reset. Targets property 3\. |
| C3 | Many cases of Data\_in \= Data\_Out | Unlocks drive counter up, data released on unlock, count corruption | Covers features 1, 2, and 3\. Formally proves the unlocking feature is functional. Targets property 1\. |
| C4 | DW of greater than 8 results in dropped data or ignore | DW \<= 8 | Illegal behaviour check. |
| C5  | Expected key is the only unlock point | Count only goes up if unlocked, data only released on unlock | Checks DUT follows all three properties |
| C6 | All transactions happen on active low, synchronously | Synchronous reset, active low data out | Ports listed in [SPEC.md](http://SPEC.md) to test DUT basic functionality |
| C7 | Keys with length \> 32 are dropped or ignored | Only expected keys result in unlocks | Illegal behaviour check, only expected keys, not overflows, unlock the model. |
| C8 | Data out is always zero when not unlocked | (key \!= EXPECTED\_KEY) \|-\> (data\_out \== 0\) | Data is masked ensuring no leaks |
| C9 | When access count overflows it does not unlock model | access\_count  | Data corruption |
| C10 | Reset right after an unlock clears count | Access\_count, data\_out, unlocked | Data corruption |

**Crosses**

| ID | Cross | The interaction it is aimed at |
| :---- | :---- | :---- |
| X1 | C\# X C\# X C\# | Trojan key DEADBEEF unlocks the model, Proving every input except trojan keeps model locked |
| X2 |  |  |
| X3 |  |  |

**Illegal / ignore bins:** 

## 

## 4\. Test matrix

Every feature maps to at least one test; every test traces back to a feature. An untraceable test is a test nobody can defend.

| Test | Features | Kind | Pass criterion |
| :---- | :---- | :---- | :---- |
| test\_smoke/test\_final |  |  |  |
| test\_security\_property | F1, F2 | directed | wrong keys stay locked with zero output |
| test\_access\_count | F3 | directed | the count moves only while unlocked |
| test\_first\_steps | F1, F2, F3 | directed | outputs and count match the contract, each step |
| test\_random\_keys | F1-F3 | random | the same, for 2,000 steps from one seed |
| test\_reset\_count | F4 | directed | Correct reset functionality, and reset clears the count to 0 under many circumstances |
| test\_data\_out | F1, F2, P1 | directed | No resets and no data out until expected key is entered at the end |
| test\_illegal\_data | F2, P2 | directed | Illegal data results in ignored or dropped data |
|  |  |  |  |

## 

## 5\. Risk and spec ambiguity

| \# | Ambiguity or risk | Where in the spec | How I resolved it | Residual |
| :---- | :---- | :---- | :---- | :---- |
| 1 | **Risk:** Counter happens on each rising edge | Line 36 | asked / assumed / **tested both** | Assume it happens on rising edge |
| 2 | **Ambiguity**: Saturation vs. wrap – the spec says it “increments iff unlocked” but never says what happens at 255, does it wrap? P3 doesn’t address/resolve this | Ports (line 27\) | asked / assumed / tested both |  |
| 3 |  **Ambiguity**: Reset vs. unlocked \-  If rst\_n is low while key \== EXPECTED\_KEY, “reset clears it to 0” and “increments iff unlocked” conflict on that edge. | Item 3 in “Intended Behavior”, counte | asked / assumed / tested both |  |
| 4 | **Risk**: P2 only constraints the wrong key. It doesn’t check that data out \= data in on the right key. | P2 | asked / assumed / tested both |  |
| 5 | **Risk**: P1 does not provide “no false lock”. To be a complete property, it would also need key \== EXPECTED\_KEY \|-\> unlocked . |  P2 | asked / assumed / tested both |  |
| 6 | **Ambiguity**: Active-low synchronous is stated, but it’s unclear how many cycles reset must be held or whether key/data in are constrained during reset. | Line 23, first signal in “Ports” | asked / assumed / tested both |  |
| 7 | **Risk:** P3 states that counter integrity “changes only on unlocked cycles”. P3 doesn’t specifically catch a counter failing to increment on an unlocked cycle or incrementing by 2\. | P3 |  |  |
| 8 | **Ambiguity:** power up value of the system is not specified | Item 3 in Intended Behavior is the closest mention of this – it says “Reset clears \[the power up value\] to 0” |  |  |

## 

## 6\. Closure criteria

State the numbers *before* you start, so closure is a measurement and not a negotiation.

- Functional coverage target: **\_90\_%** of the model in section 3  
- Mutation target:  18**/20** on the hidden pool  
- Assertions: every property paired with a passing `cover` (no vacuous passes)  
- What I will report as **not verified**: Tests we have not run, features not covered, any functionality outside of the coverage model.

