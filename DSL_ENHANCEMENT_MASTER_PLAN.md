# DSL Enhancement Master Plan

**Date**: 2025-12-08
**Version**: 1.0.0
**Target**: mysingle.dsl package enhancement for Strategy/Indicator/Backtest services

---

## 1. Executive Summary

### 1.1 Current State

**Package Location**: `packages/mysingle-pack/src/mysingle/dsl/`

**Core Components**:
- `parser.py` - RestrictedPython-based compiler
- `executor.py` - Sandboxed execution engine
- `validator.py` - Security & AST validation
- `stdlib.py` - Standard library functions (60+)
- `limits.py` - Resource quota management
- `errors.py` - Exception hierarchy

**Current Users**:
- **Strategy Service**: DSL validation & compilation (validation/stages/dsl.py)
- **Indicator Service**: DSL compiler service for custom indicators
- **Backtest Service**: DSL execution via StrategyEvaluator

### 1.2 Critical Findings

**Architecture Issues**:
1. **Inconsistent Integration**: Each service implements its own wrapper (StrategyDSLService, DSLCompilerService, StrategyEvaluator)
2. **Incomplete Documentation**: DSL spec scattered across 3 services with conflicting examples
3. **Missing Features**: No AST-based type inference, limited stdlib for strategy-specific operations
4. **Version Fragmentation**: No unified DSL version policy across services

**Usage Patterns**:
- Strategy: Parse → Validate → Store bytecode (no execution in service)
- Indicator: Parse → Validate → Execute → Cache result
- Backtest: Load bytecode → Execute → Generate signals

---

## 2. Problem Diagnosis

### 2.1 Technical Debt

**P1 - Critical**:
- ❌ No type inference system (manual param validation required)
- ❌ Security validator doesn't catch all reflection attacks
- ❌ Resource limits not enforced on Windows (signal.SIGALRM unavailable)
- ❌ Stdlib functions lack comprehensive docstrings

**P2 - High**:
- ⚠️ Bytecode serialization format not version-tracked
- ⚠️ No caching layer for compiled code
- ⚠️ Error messages lack line/column precision
- ⚠️ Missing profiling/instrumentation hooks

**P3 - Medium**:
- ⚠️ Limited pandas/numpy function whitelisting
- ⚠️ No support for multi-output strategies (e.g., long + short signals)
- ⚠️ Stdlib functions not categorized by use case

### 2.2 Integration Gaps

**Service-Level Issues**:

| Service   | Integration Status        | Missing Features                       |
| --------- | ------------------------- | -------------------------------------- |
| Strategy  | ✅ Compile/Validate        | Execution runtime, Type hints          |
| Indicator | ✅ Full pipeline           | Performance profiling, Batch execution |
| Backtest  | ⚠️ Partial (custom parser) | Unified DSL interface, Error recovery  |

**Cross-Service Concerns**:
- No shared DSL version negotiation
- Inconsistent parameter passing (dict vs kwargs)
- Different error handling strategies
- No centralized DSL registry

### 2.3 Documentation Fragmentation

**Existing Docs (Duplicated/Conflicting)**:
- `mysingle-pack/src/mysingle/dsl/README.md` (1408 lines)
- `strategy-service/docs/DSL/STRATEGY_DSL_GUIDE.md` (1262 lines)
- `indicator-service/docs/dsl_intro/03_DSL_SPECIFICATION.md` (1227 lines)

**Inconsistencies**:
- Function signatures differ (e.g., `RSI(series, period)` vs `RSI(data, params)`)
- Security restrictions documented differently
- Version numbers out of sync (1.0.0 vs 1.3.0)

---

## 3. Enhancement Strategy

### 3.1 Phase 1: Core Runtime Hardening (4 weeks)

**Goal**: Production-grade stability & security

**M1.1 Security Enhancements**:
- Implement comprehensive AST visitor for all dangerous patterns
- Add runtime sandboxing for attribute access (`__class__`, `__bases__`)
- Whitelist safe pandas/numpy operations explicitly
- Add bytecode signature validation

**M1.2 Type System Foundation**:
- Build AST-based type inference engine
- Define type schemas for OHLCV data, indicators, signals
- Implement static type checking before compilation
- Generate type hints from DSL code

**M1.3 Cross-Platform Resource Limits**:
- Implement threading-based timeout for Windows
- Add memory profiling hooks (psutil/resource)
- Create quota enforcement middleware
- Build resource usage reporting

**M1.4 Error Handling Improvements**:
- Parse AST to extract line/column info for all errors
- Implement error recovery suggestions
- Add structured error codes (DSL-001, DSL-002, etc.)
- Create user-friendly error messages

### 3.2 Phase 2: Standard Library Expansion (3 weeks)

**Goal**: Rich DSL vocabulary for quant strategies

**M2.1 Technical Indicators**:
- Add missing indicators: Ichimoku, Pivot Points, Fibonacci retracements
- Implement vectorized operations for performance
- Create indicator composition helpers (e.g., `combine_signals`)

**M2.2 Strategy Primitives**:
- `position_sizing()` - Kelly criterion, fixed fractional
- `risk_management()` - Stop loss, take profit, trailing stops
- `signal_filters()` - Regime detection, volatility adjustment
- `portfolio_logic()` - Multi-asset position allocation

**M2.3 Utility Functions**:
- Time/date helpers: `is_trading_day()`, `get_session()`
- Data validation: `check_missing_data()`, `detect_outliers()`
- Statistical tests: `test_stationarity()`, `correlation_matrix()`

**M2.4 Documentation**:
- Auto-generate function catalog from docstrings
- Create interactive API reference
- Build DSL playground for testing

### 3.3 Phase 3: Service Integration Unification (4 weeks)

**Goal**: Single source of truth for DSL execution

**M3.1 Unified Service Interface**:
- Create `DSLRuntimeService` base class
- Standardize compile/execute/validate methods
- Implement plugin system for service-specific extensions
- Define gRPC proto for DSL operations

**M3.2 Version Management**:
- Implement DSL schema versioning (semantic versioning)
- Build migration tools for version upgrades
- Add compatibility layer for legacy code
- Create version negotiation protocol

**M3.3 Caching Layer**:
- Redis-based bytecode cache (key: code_hash)
- Distributed cache invalidation strategy
- Cache warming for popular indicators
- Performance metrics collection

**M3.4 Service Refactoring**:
- Migrate StrategyDSLService to use DSLRuntimeService
- Refactor DSLCompilerService to unified interface
- Update StrategyEvaluator to use gRPC proto
- Deprecate custom parsers

### 3.4 Phase 4: Advanced Features (5 weeks)

**Goal**: Enterprise-grade DSL platform

**M4.1 Graph-Based Compilation**:
- Build dependency graph from DSL code
- Optimize execution order (topological sort)
- Parallel execution for independent indicators
- Dead code elimination

**M4.2 JIT Optimization**:
- Identify hot paths via profiling
- Generate optimized bytecode for repeated operations
- Cache intermediate results intelligently
- Implement lazy evaluation for expensive ops

**M4.3 Debugging Tools**:
- Interactive debugger for DSL code
- Step-through execution with variable inspection
- Performance profiler with flamegraphs
- Unit test framework for DSL code

**M4.4 Template & Macro System**:
- Define reusable strategy templates
- Macro expansion for common patterns
- Template validation and testing
- Community template sharing

---

## 4. Implementation Priorities

### 4.1 Critical Path (Must-Have)

**Week 1-2**:
- [ ] Security audit & hardening (M1.1)
- [ ] Cross-platform resource limits (M1.3)
- [ ] Error message improvements (M1.4)

**Week 3-4**:
- [ ] Type inference foundation (M1.2)
- [ ] Unified service interface design (M3.1)
- [ ] Version management system (M3.2)

**Week 5-7**:
- [ ] Standard library expansion (M2.1, M2.2)
- [ ] Caching layer implementation (M3.3)

**Week 8-10**:
- [ ] Service refactoring rollout (M3.4)
- [ ] Documentation consolidation
- [ ] Integration testing across all services

**Week 11-16**:
- [ ] Advanced features based on usage metrics (M4.x)
- [ ] Performance optimization
- [ ] Production deployment

### 4.2 Nice-to-Have (Future Releases)

- Graph visualization for DSL dependencies
- AI-assisted DSL code generation
- Multi-language DSL support (JS, Rust)
- Cloud-native DSL execution (serverless)

---

## 5. Risk Mitigation

### 5.1 Technical Risks

| Risk                                 | Probability | Impact   | Mitigation                              |
| ------------------------------------ | ----------- | -------- | --------------------------------------- |
| Breaking changes in RestrictedPython | Medium      | High     | Pin version, maintain fork              |
| Performance regression               | High        | Medium   | Comprehensive benchmarks, rollback plan |
| Security vulnerabilities             | Low         | Critical | Red team testing, bug bounty            |
| Service integration failures         | Medium      | High     | Gradual rollout, feature flags          |

### 5.2 Operational Risks

| Risk                     | Probability | Impact | Mitigation                                    |
| ------------------------ | ----------- | ------ | --------------------------------------------- |
| Documentation lag        | High        | Medium | Auto-generate docs, CI enforcement            |
| Version incompatibility  | Medium      | High   | Strict versioning policy, deprecation notices |
| User adoption resistance | Low         | Medium | Migration guides, backward compatibility      |

---

## 6. Success Metrics

### 6.1 Technical KPIs

- **Performance**: DSL execution < 2x native Python
- **Reliability**: 99.9% uptime, < 0.1% error rate
- **Security**: 0 critical vulnerabilities, pass all audits
- **Coverage**: 90%+ test coverage for core DSL

### 6.2 Business KPIs

- **Adoption**: 80%+ of strategies use DSL by Q2 2026
- **Productivity**: 50% reduction in strategy development time
- **Quality**: 30% reduction in backtest runtime errors

### 6.3 Monitoring

- DSL compilation success rate (by service)
- Execution time percentiles (p50, p95, p99)
- Memory usage distribution
- Error type frequency
- Cache hit ratio

---

## 7. Governance

### 7.1 Ownership

- **DSL Core**: Platform Team
- **Stdlib Functions**: Quant Research Team
- **Service Integration**: Backend Team
- **Documentation**: DevRel Team

### 7.2 Change Management

**Minor Changes** (stdlib functions, docs):
- PR review by 1 core maintainer
- Automated tests must pass
- Deploy to staging → production

**Major Changes** (parser, executor, security):
- Design review by 2+ senior engineers
- Security audit required
- Gradual rollout with canary deployment
- Rollback plan documented

### 7.3 Communication

- Bi-weekly DSL working group meetings
- Monthly changelog published to all services
- Quarterly roadmap review with stakeholders
- Dedicated Slack channel: #dsl-platform

---

## 8. Appendix

### 8.1 Current DSL Stats

- **Total Functions**: 60+ (stdlib.py)
- **Services Using DSL**: 3 (Strategy, Indicator, Backtest)
- **Lines of Code**: ~2,000 (core runtime)
- **Test Coverage**: ~75% (needs improvement)
- **Documentation Pages**: 12+ (fragmented)

### 8.2 References

- RestrictedPython: https://restrictedpython.readthedocs.io/
- Strategy Service AGENTS.md
- Indicator Service DSL specs
- Backtest Service Phase 5.7 docs
- MySingle Platform guidelines

---

**Status**: Draft for Review
**Next Review**: 2025-12-15
**Approval Required**: CTO, VP Engineering, Tech Leads
