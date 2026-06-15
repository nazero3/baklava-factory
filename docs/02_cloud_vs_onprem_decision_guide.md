# Baklava Factory Deployment Decision Guide

## Objective
Select the right deployment model based on business priorities, not technical complexity.

## Option A: Cloud (Online)
### Best When
- Management wants access from anywhere
- The business wants faster rollout and easier future scaling
- Internal IT team is limited

### Validity Requirements
- Reliable internet in factory and stores
- 4G backup router at each site
- Domain and SSL certificate
- Managed cloud hosting account
- Security policy: strong passwords, role permissions, manager MFA
- Data backup policy (daily backup, restore testing monthly)

### Operational Commitments
- Monthly hosting and support budget
- Internet continuity monitoring

## Option B: On-Premise (Company-Only / Offline-First)
### Best When
- Business policy requires full local data control
- Sites may face frequent internet instability
- Company accepts infrastructure ownership

### Validity Requirements
- Dedicated server hardware (production + optional standby)
- UPS with graceful shutdown plan
- NAS or external encrypted backup storage
- Firewall and endpoint protection
- VPN connectivity between factory and stores
- Local IT administration for updates and backup checks
- Disaster recovery drill each quarter

### Operational Commitments
- Hardware lifecycle and replacement budget
- Ongoing IT maintenance contract

## Comparison Matrix (Non-Technical)
| Decision Factor | Cloud | On-Premise |
|---|---|---|
| Initial Cost | Lower | Higher |
| Ongoing Cost | Monthly predictable | IT maintenance + periodic upgrades |
| Speed to Start | Faster | Slower |
| Data Control | Shared responsibility | Full local control |
| Scalability | Easier | Manual infrastructure expansion |
| Dependency | Internet availability | Internal IT capability |
| Best for This Project | Strong fit | Premium alternative |

## Recommended Decision for Medium Scale (1 Factory + 3 Stores, 16-40 Users)
- Primary recommendation: Cloud-first
- Fallback/alternative: On-premise if governance requires local-only data

## Final Decision Workshop (60 minutes)
1. Confirm compliance expectations
2. Confirm budget model preference (CAPEX vs OPEX)
3. Review internet reliability per location
4. Review IT support capability
5. Sign deployment decision

## Decision Output
- Signed deployment model (Cloud or On-Premise)
- Risk register with mitigation owners
- Approved infrastructure procurement list (if on-premise)
