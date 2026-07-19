# Mission-Interface Threat Model

## Protected boundary

The protected boundary is the transition from language-level intent to a control-facing mission contract. The deterministic gate must run after any rule-based or learned parser and before a navigation or flight-control adapter.

## Failure modes

| Failure mode | Example | Mitigation in this repository |
|---|---|---|
| Missing constraint | No obstacle clearance stated | Non-finite clearance is blocked |
| Unsafe explicit value | 0.4 m clearance | Versioned numerical limits |
| Unsupported action | Unknown mission type | Allow-list for mission types |
| Aggressive command | High-speed request | Speed-mode allow-list |
| Missing fail-safe | No behavior on link loss | Mandatory return-to-home flag |
| Perception uncertainty ignored | Continue on low LiDAR confidence | Mandatory stop flag |
| Schema drift | Agent emits a different contract version | Exact protocol-version check |
| Gate bypass | Agent sends directly to control | Architecture requires adapter to accept only validated contracts |

## Out of scope

This policy does not prove that return-to-home or stopping is implemented correctly by a flight controller. It does not authenticate the operator, protect the communications channel, validate geofences, or reason over live obstacles. Those are additional layers that must be tested on the physical system.
