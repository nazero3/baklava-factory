# Engineering Team Structure and Specialized Hiring Plan

## Decision

Hire three local engineering agents with strict single-responsibility boundaries. The team is designed around the 64K-token context limit on local Hermes Qwen 3.5 workers: each agent owns one narrow domain, receives scoped handoffs, and does not accumulate unrelated implementation context.

## Operating model

- Split work by domain before implementation starts.
- Give each agent only the artifacts needed for its specialty.
- Require typed or documented contracts between domains before parallel work begins.
- Route cross-domain conflicts through the CEO/CTO instead of letting agents negotiate large shared context.
- Keep each handoff durable: objective, owner, inputs, outputs, acceptance criteria, blockers, and next action.

## Proposed engineering team

### Agent 1: UI Layout Specialist

**Mission:** Build pure visual component templates and static presentation layers.

**Owns**

- HTML/JSX structure for static components.
- CSS, layout, spacing, visual hierarchy, responsive presentation.
- Design-system component composition when no runtime state is required.
- Story/static preview examples that demonstrate visual states with fixed props.

**Does not own**

- Custom hooks, global stores, API calls, routing, persistence, authentication, or test strategy.
- Business rules or data transformation beyond display formatting explicitly provided in props.

**Primary outputs**

- Presentational components with documented props.
- Static fixtures/mock props for preview.
- Visual implementation notes and unresolved design questions.

### Agent 2: State & Logic Specialist

**Mission:** Own application data flow without rendering UI.

**Owns**

- Custom hooks, global state architecture, client-side data models, and API fetching layers.
- Cache invalidation, loading/error state contracts, mutations, and data normalization.
- Business logic and derived state needed by UI and routing layers.

**Does not own**

- Component markup, CSS, static layout, route maps, navigation shells, or visual presentation.

**Primary outputs**

- Hooks/services/stores with typed interfaces.
- Data-flow diagrams or notes for integration.
- Mockable contracts consumed by UI and routing agents.

### Agent 3: Routing & Core Integration Specialist

**Mission:** Connect pages, routes, providers, and domain contracts into a coherent application shell.

**Owns**

- System route maps, page architecture, navigation hierarchy, and app-level provider composition.
- Integration of UI Layout outputs with State & Logic contracts.
- Boundary enforcement between route, UI, and state layers.
- Core error/loading shells that are required at the route level.

**Does not own**

- Designing visual components from scratch, implementing data-fetching internals, or writing broad QA strategy.

**Primary outputs**

- Route definitions and page-level integration modules.
- Integration checklists for UI/state contracts.
- Escalations when contracts are incomplete or cross-domain decisions are needed.

## Handoff protocol

1. CTO or CEO decomposes the feature into UI, state, and routing workstreams.
2. State & Logic Specialist defines data contracts first when runtime behavior is material.
3. UI Layout Specialist builds visual components against stable props or mocked fixtures.
4. Routing & Core Integration Specialist wires the route shell after contracts are available.
5. Any task that requires an agent to cross its boundary is escalated rather than absorbed.

## Hire requests for board inbox

### Hire request: UI Layout Specialist

Please approve hiring a **UI Layout Specialist** local agent.

- **Reason:** Preserve the 64K-token context budget by isolating static visual implementation from state, routing, and testing concerns.
- **Scope:** Pure component templates, HTML/CSS structure, static presentation components, responsive layout, and visual fixtures.
- **Restrictions:** No custom hooks, API fetching, global state, routing, or business logic.
- **Success criteria:** Produces presentational components with clear prop contracts and can complete layout tasks without loading application state or routing context.

### Hire request: State & Logic Specialist

Please approve hiring a **State & Logic Specialist** local agent.

- **Reason:** Keep data-flow complexity isolated so UI and routing agents do not saturate their 64K-token context windows.
- **Scope:** Custom hooks, global state management, API fetching layers, cache/mutation behavior, data normalization, and business logic contracts.
- **Restrictions:** No UI rendering, CSS, visual layout, or route-map ownership.
- **Success criteria:** Produces mockable hooks/services/stores with stable contracts that UI and routing agents can consume without understanding implementation internals.

### Hire request: Routing & Core Integration Specialist

Please approve hiring a **Routing & Core Integration Specialist** local agent.

- **Reason:** Centralize route maps and application shell integration without forcing UI or state agents to absorb full-system context.
- **Scope:** Route definitions, page architecture, provider wiring, navigation hierarchy, and integration of UI/state contracts.
- **Restrictions:** No pure visual component design from scratch and no data-fetching internals unless limited to route-level wiring.
- **Success criteria:** Produces coherent page shells and route integrations while enforcing boundaries between presentation and state work.

## CEO recommendation

Approve all three hires as a single modular engineering pod. This structure directly addresses the local hardware constraint by preventing one agent from carrying layout, data, routing, and integration context simultaneously.
