# PR mirror — thebrazenbeard/vera#95

Title: `review: validate restored observation lineage on current head`
State: OPEN / DRAFT / TEST-ONLY HOSTILE SUCCESSOR
Base SHA at cut: `af9270f3df4d779b29abca5740000036c7250b32`
Head SHA: `31a28ffeaa2f979fd3536a049c4fe84a0847fc49`

Purpose: current-head rebind of the durable-Q3 restore-lineage finding. A fresh QUIESCENT/noneligible record may not restore with forged `last_observation_qualifying=true`, while a real zero-time qualifying endpoint must remain restorable and able to continue persistence on the next bounded trusted interval.

No merge, deployment, provider mutation, qualification, install/cutover, authority promotion, memory promotion, phenomenology promotion, or paid CI action performed.
