## FAS Mode Hex Identifier

Each SPICE library is labeled with a **hexadecimal identifier** that reflects the combination of annotation tools used for FAS scoring. This identifier helps differentiate libraries generated with different tool configurations.

The identifier is computed using a bitmask approach. Each annotation tool corresponds to one position in a bit array. If a tool was used during scoring, its respective bit is set to `1`; otherwise, it remains `0`. The complete bit array is then converted to a hexadecimal string, which becomes the **FAS mode hex code**.

### How It Works

The identifier is computed using the `FASModeHex` class.

- Internally, the system uses **12 bits** (3 bytes).
- The **first 2 bits** are reserved and unused (`blocked_bits`).
- The remaining **10 bits** represent the enable/disable state of 10 specific analysis modes.
- These 12 bits are grouped into 3 segments of 4 bits each (nibbles), and each group is converted into a hexadecimal character.
- This results in a **3-character hex string** (e.g., `3ee`, `000`, `1c0`).

The mapping of bits to modes is fixed and always starts at bit index `2`:

| Bit Index | Mode Name     | Used |
| --------- | ------------- | ---- |
| 0         | (reserved)    | No   |
| 1         | (reserved)    | No   |
| 2         | `#linearized` | Yes  |
| 3         | `Pfam`        | Yes  |
| 4         | `SMART`       | Yes  |
| 5         | `#normal`     | Yes  |
| 6         | `fLPS`        | Yes  |
| 7         | `COILS2`      | Yes  |
| 8         | `SEG`         | Yes  |
| 9         | `SignalP`     | Yes  |
| 10        | `TMHMM`       | Yes  |
| 11        | `#checked`    | Yes  |

---

## Example Hex Identifier Mapping

The table below shows a few examples of different mode combinations and the resulting hexadecimal string.

| Enabled Modes         | Bit Pattern    | Hex Identifier |
| --------------------- | -------------- | -------------- |
| _(none)_              | `000000000000` | `000`          |
| `#linearized`, `Pfam` | `001100000000` | `300`          |
| All modes enabled     | `001111111111` | `3ee`          |

Since you usually want to use all available annotation tools, the identifier should be `3ee` in most cases.
